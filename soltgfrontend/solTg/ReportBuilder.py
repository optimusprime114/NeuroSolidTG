import os
import re
import glob
import argparse
import pandas as pd
from jinja2 import Template
from datetime import datetime


class ModernReportBuilder:
    # pass
    def __init__(self, output_dir, sandbox_dir):
        self.sandbox_dir = os.path.abspath(sandbox_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.data = []

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _read_file_safe(self, filepath):
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, "r", encoding='ISO-8859-1') as f:
                    return f.read()
            except:
                return None

    def _truncate_content(self, content, limit=10000):
        """Helper to truncate large text content."""
        if content and len(content) > limit:
            return content[:limit] + f"\n\n... [TRUNCATED - Content exceeded {limit} chars] ..."
        return content

    def _get_smt2_info(self, directory):
        """Returns list of dicts with content for all .smt2 files."""
        smt2_files = glob.glob(os.path.join(directory, "*.smt2"))
        info = []
        for f in smt2_files:
            name = os.path.basename(f)
            raw_content = self._read_file_safe(f)
            
            # Count lines before truncating so line count is accurate
            try:
                line_count = len(raw_content.splitlines()) if raw_content else 0
            except:
                line_count = "-"
            
            # Truncate content for display
            display_content = self._truncate_content(raw_content, limit=10000)
            
            info.append({
                'name': name,
                'lines': line_count,
                'path': f,
                'content': display_content
            })
        return info

    def _extract_llm_data(self, directory, prefix):
        """Generic extractor for llm_input_* or llm_output_* files."""
        items = []
        # Pattern: prefix + digit + anything (e.g., llm_input_1.txt)
        files = glob.glob(os.path.join(directory, f"{prefix}*"))
        
        for f_path in files:
            fname = os.path.basename(f_path)
            # Regex to capture the number after the prefix (e.g., llm_input_5 -> 5)
            match = re.search(rf'{prefix}(\d+)', fname)
            if match:
                seq_len = match.group(1)
                raw_content = self._read_file_safe(f_path)
                
                # Truncate if it's an input file (prefix 'llm_input_')
                # You can apply this to outputs too if you want, but you specifically asked for inputs
                content = raw_content.strip() if raw_content else "Empty File"
                if "llm_input" in prefix:
                     content = self._truncate_content(content, limit=10000)

                items.append({
                    'sequence_length': int(seq_len),
                    'content': content,
                    'file_path': f_path
                })
        return sorted(items, key=lambda x: x['sequence_length'])

    def _extract_log_metrics(self, directory):
        log_path = os.path.join(directory, 'log.txt')
        time_val = "N/A"
        z3_status = "-"
        content = None
        
        if os.path.exists(log_path):
            content = self._read_file_safe(log_path)
            if content:
                if "z3_error" in content: z3_status = "timeout"
                elif "unsat" in content: z3_status = "unsat"
                elif "sat" in content: z3_status = "sat"
                
                lines = content.splitlines()
                if lines:
                    last_line = lines[-1]
                    if "total time" in last_line:
                        parts = last_line.split()
                        if len(parts) > 2: time_val = float(parts[2])
        return time_val, z3_status, content

    def _find_generated_test(self, directory):
        """Finds path and content of .t.sol file."""
        all_sol = glob.glob(os.path.join(directory, "*.t.sol"))
        if all_sol:
            path = all_sol[0]
            return path, self._read_file_safe(path)
        return None, None

    def _process_directory(self, path):
        # 1. Identify Source File (.sol)
        all_sols = glob.glob(os.path.join(path, "*.sol"))
        source_sols = [s for s in all_sols if not s.endswith('.t.sol')]
        
        contract_name = os.path.basename(path)
        sol_path = None
        sol_content = None
        
        if source_sols:
            source_sols.sort(key=len)
            contract_name = os.path.basename(source_sols[0])
            sol_path = source_sols[0]
            sol_content = self._read_file_safe(sol_path)

        # 2. Extract Data
        time_val, z3_status, log_content = self._extract_log_metrics(path)
        
        # New: Extract Inputs AND Outputs
        llm_inputs = self._extract_llm_data(path, "llm_input_")
        llm_vulns = self._extract_llm_data(path, "llm_output_")
        
        smt2_info = self._get_smt2_info(path)
        gen_test_path, gen_test_content = self._find_generated_test(path)
        
        # 3. Locate Test Log Content
        test_log_path = None
        test_log_content = None
        if os.path.exists(os.path.join(path, "test_results.txt")):
            test_log_path = os.path.join(path, "test_results.txt")
        
        if test_log_path:
            test_log_content = self._read_file_safe(test_log_path)

        row = {
            'contract_name': contract_name,
            'dir_path': path,
            'sol_path': sol_path,
            'sol_content': sol_content,
            'time_seconds': time_val,
            'z3_status': z3_status,
            'llm_inputs': llm_inputs,   # List of dicts
            'llm_vulns': llm_vulns,     # List of dicts
            'vuln_count': len(llm_vulns),
            'smt2_info': smt2_info,
            'generated_test_path': gen_test_path,
            'generated_test_content': gen_test_content,
            'log_content': log_content,
            'test_log_content': test_log_content
        }
        self.data.append(row)
    
    def scan(self):
        print(f"Scanning Sandbox: {self.sandbox_dir}")
        is_flat = False
        if glob.glob(os.path.join(self.sandbox_dir, "*.sol")) or os.path.exists(os.path.join(self.sandbox_dir, "log.txt")):
            is_flat = True

        if is_flat:
            print(" -> Detected Flat structure.")
            self._process_directory(self.sandbox_dir)
        else:
            print(" -> Detected Nested structure.")
            subdirs = [f.path for f in os.scandir(self.sandbox_dir) if f.is_dir()]
            for s in subdirs:
                self._process_directory(s)
        print(f" -> Found {len(self.data)} entries.")
    
    def generate_excel(self):
        if not self.data: return
        print(f"Generating Excel in {self.output_dir}...")
        
        rows = []
        for d in self.data:
            input_summary = " | ".join([f"Seq {i['sequence_length']}: {i['content'][:50]}..." for i in d['llm_inputs']])
            vuln_summary = " | ".join([f"Seq {v['sequence_length']}: {v['content'][:50]}..." for v in d['llm_vulns']])
            smt_summary = ", ".join([f"{s['name']}" for s in d['smt2_info']])
            
            rows.append({
                'Contract': d['contract_name'],
                'Time (s)': d['time_seconds'],
                'Z3 Status': d['z3_status'],
                'LLM Inputs': input_summary,
                'LLM Output': vuln_summary,
                'Generated Test File': os.path.basename(d['generated_test_path']) if d['generated_test_path'] else "Safe - No Tests",
                'SMT2 Files': smt_summary,
                'Source Path': d['sol_path']
            })
            
        df = pd.DataFrame(rows)
        out_path = os.path.join(self.output_dir, "Final_Report.xlsx")
        writer = pd.ExcelWriter(out_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Summary', index=False)
        
        ws = writer.sheets['Summary']
        for i, col in enumerate(df.columns):
            max_len = min(50, max(df[col].astype(str).map(len).max(), len(col)) + 2)
            ws.set_column(i, i, max_len)
        writer.close()
        print(f"Excel saved: {out_path}")
    
    def generate_html(self):
        if not self.data: return
        print(f"Generating HTML in {self.output_dir}...")
        
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Analysis Report</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css" rel="stylesheet">
            <style>
                body { background: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
                .card { box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: none; margin-bottom: 20px; }
                pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 6px; max-height: 600px; overflow: auto; }
                .modal-xl { max-width: 90%; }
            </style>
        </head>
        <body class="p-4">
        
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1>🛡️ NeuroSolidTG Report</h1>
                <p class="text-muted mb-0">Analysis & Verification Results</p>
            </div>
            <span class="text-muted">{{ timestamp }}</span>
        </div>

        <div class="card p-4">
            <table id="mainTable" class="table table-striped align-middle">
                <thead class="table-dark">
                    <tr>
                        <th style="width: 15%">Contract</th>
                        <th>Metrics</th>
                        <th>SMT2 Info</th>
                        <th>LLM Inputs</th>
                        <th>LLM Output</th>
                        <th>Generated Test Suite</th>
                        <th>Logs</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        <td>
                            <strong>{{ row.contract_name }}</strong><br>
                            {% if row.sol_content %}
                                <button class="btn btn-primary btn-sm mt-1" data-bs-toggle="modal" data-bs-target="#solModal{{ loop.index }}">
                                    📄 View .sol
                                </button>
                            {% else %}
                                <span class="badge bg-secondary">No Source</span>
                            {% endif %}
                        </td>

                        <td>
                            <div>⏱️ <strong>{{ row.time_seconds }}s</strong></div>
                            <div class="mt-1">
                                <span class="badge {% if row.z3_status == 'sat' %}bg-danger{% elif row.z3_status == 'unsat' %}bg-success{% else %}bg-secondary{% endif %}">
                                    {{ row.z3_status }}
                                </span>
                            </div>
                        </td>

                        <td>
                            {% if row.smt2_info %}
                                {% for s in row.smt2_info %}
                                    <div class="mb-1">
                                        <button class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#smtModal{{ loop.index }}_{{ loop.index0 }}">
                                            {{ s.name }}
                                        </button>
                                        <span class="text-muted" style="font-size:0.8em">({{ s.lines }}L)</span>
                                    </div>
                                {% endfor %}
                            {% else %}
                                <span class="text-muted">-</span>
                            {% endif %}
                        </td>

                        <td>
                            {% if row.llm_inputs %}
                                {% for inp in row.llm_inputs %}
                                    <button class="btn btn-sm btn-outline-primary mb-1" 
                                            data-bs-toggle="modal" data-bs-target="#inputModal{{ loop.index }}_{{ inp.sequence_length }}">
                                        Seq {{ inp.sequence_length }}
                                    </button>
                                {% endfor %}
                            {% else %}
                                <span class="text-muted">No Inputs</span>
                            {% endif %}
                        </td>

                        <td>
                            {% if row.llm_vulns %}
                                {% for v in row.llm_vulns %}
                                    <button class="btn btn-sm btn-outline-danger mb-1" 
                                            data-bs-toggle="modal" data-bs-target="#vulnModal{{ loop.index }}_{{ v.sequence_length }}">
                                        Seq {{ v.sequence_length }}
                                    </button>
                                {% endfor %}
                            {% else %}
                                <span class="badge bg-success">Clean</span>
                            {% endif %}
                        </td>

                        <td>
                            {% if row.generated_test_content %}
                                <button class="btn btn-success btn-sm" data-bs-toggle="modal" data-bs-target="#testFileModal{{ loop.index }}">
                                    🧪 View .t.sol
                                </button>
                            {% else %}
                                <span class="badge bg-success">No tests generated<br>Check the LLM Output to see final verdict.</span>
                            {% endif %}
                        </td>

                        <td>
                            <div class="d-grid gap-2">
                                {% if row.log_content %}
                                    <button class="btn btn-sm btn-light border" data-bs-toggle="modal" data-bs-target="#logModal{{ loop.index }}">
                                        📄 log.txt
                                    </button>
                                {% endif %}
                                
                                {% if row.test_log_content %}
                                    <button class="btn btn-sm btn-dark" data-bs-toggle="modal" data-bs-target="#foundryLogModal{{ loop.index }}">
                                        🔨 Foundry output
                                    </button>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {% for row in data %}
        
            {% if row.sol_content %}
            <div class="modal fade" id="solModal{{ loop.index }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Source: {{ row.contract_name }}</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ row.sol_content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endif %}

            {% for s in row.smt2_info %}
            <div class="modal fade" id="smtModal{{ loop.index }}_{{ loop.index0 }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">{{ s.name }}</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ s.content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endfor %}

            {% for inp in row.llm_inputs %}
            <div class="modal fade" id="inputModal{{ loop.index }}_{{ inp.sequence_length }}" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">LLM Input (Seq {{ inp.sequence_length }})</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <h6>{{ row.contract_name }}</h6>
                            <pre>{{ inp.content }}</pre>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}

            {% for v in row.llm_vulns %}
            <div class="modal fade" id="vulnModal{{ loop.index }}_{{ v.sequence_length }}" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-danger text-white">
                            <h5 class="modal-title">Vulnerability (Seq {{ v.sequence_length }})</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <h6>{{ row.contract_name }}</h6>
                            <pre>{{ v.content }}</pre>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}

            {% if row.generated_test_content %}
            <div class="modal fade" id="testFileModal{{ loop.index }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">Generated Test: {{ row.contract_name }}.t.sol</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ row.generated_test_content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endif %}

            {% if row.log_content %}
            <div class="modal fade" id="logModal{{ loop.index }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Analysis Log: {{ row.contract_name }}</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ row.log_content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endif %}

            {% if row.test_log_content %}
            <div class="modal fade" id="foundryLogModal{{ loop.index }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-dark text-white">
                            <h5 class="modal-title">Foundry Output: {{ row.contract_name }}</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ row.test_log_content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endif %}

        {% endfor %}

        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
        <script>
            $(document).ready(function(){
                $('#mainTable').DataTable({
                    "order": [[ 1, "desc" ]] 
                });
            });
        </script>
        </body>
        </html>
        """
        
        with open(os.path.join(self.output_dir, "NeuroSolidTG_Report.html"), "w", encoding="utf-8") as f:
            f.write(Template(template_str).render(data=self.data, timestamp=datetime.now()))
        print(f"HTML saved: {os.path.join(self.output_dir, 'NeuroSolidTG.html')}")
    
    def generate_html_2(self):
        """Simplified HTML report WITHOUT LLM Inputs/Vulns."""
        if not self.data: return
        print(f"Generating HTML (Simplified) in {self.output_dir}...")
        
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Analysis Report</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css" rel="stylesheet">
            <style>
                body { background: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
                .card { box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: none; margin-bottom: 20px; }
                pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 6px; max-height: 600px; overflow: auto; }
                .modal-xl { max-width: 90%; }
            </style>
        </head>
        <body class="p-4">
        
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1>🛡️ SolidTG Report</h1>
                <p class="text-muted mb-0">Analysis & Verification Results</p>
            </div>
            <span class="text-muted">{{ timestamp }}</span>
        </div>

        <div class="card p-4">
            <table id="mainTable" class="table table-striped align-middle">
                <thead class="table-dark">
                    <tr>
                        <th style="width: 20%">Contract</th>
                        <th>Metrics</th>
                        <th>SMT2 Info</th>
                        <th>Generated Test Suite</th>
                        <th>Logs</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        <td>
                            <strong>{{ row.contract_name }}</strong><br>
                            {% if row.sol_content %}
                                <button class="btn btn-primary btn-sm mt-1" data-bs-toggle="modal" data-bs-target="#solModal{{ loop.index }}">
                                    📄 View .sol
                                </button>
                            {% else %}
                                <span class="badge bg-secondary">No Source</span>
                            {% endif %}
                        </td>

                        <td>
                            <div>⏱️ <strong>{{ row.time_seconds }}s</strong></div>
                            <div class="mt-1">
                                <span class="badge {% if row.z3_status == 'sat' %}bg-danger{% elif row.z3_status == 'unsat' %}bg-success{% else %}bg-secondary{% endif %}">
                                    {{ row.z3_status }}
                                </span>
                            </div>
                        </td>

                        <td>
                            {% if row.smt2_info %}
                                {% for s in row.smt2_info %}
                                    <div class="mb-1">
                                        <button class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#smtModal{{ loop.index }}_{{ loop.index0 }}">
                                            {{ s.name }}
                                        </button>
                                        <span class="text-muted" style="font-size:0.8em">({{ s.lines }}L)</span>
                                    </div>
                                {% endfor %}
                            {% else %}
                                <span class="text-muted">-</span>
                            {% endif %}
                        </td>

                        <td>
                            {% if row.generated_test_content %}
                                <button class="btn btn-success btn-sm" data-bs-toggle="modal" data-bs-target="#testFileModal{{ loop.index }}">
                                    🧪 View .t.sol
                                </button>
                            {% else %}
                                <span class="badge bg-success">No tests generated</span>
                            {% endif %}
                        </td>

                        <td>
                            <div class="d-grid gap-2">
                                {% if row.log_content %}
                                    <button class="btn btn-sm btn-light border" data-bs-toggle="modal" data-bs-target="#logModal{{ loop.index }}">
                                        📄 log.txt
                                    </button>
                                {% endif %}
                                
                                {% if row.test_log_content %}
                                    <button class="btn btn-sm btn-dark" data-bs-toggle="modal" data-bs-target="#foundryLogModal{{ loop.index }}">
                                        🔨 Foundry output
                                    </button>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {% for row in data %}
        
            {% if row.sol_content %}
            <div class="modal fade" id="solModal{{ loop.index }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Source: {{ row.contract_name }}</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ row.sol_content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endif %}

            {% for s in row.smt2_info %}
            <div class="modal fade" id="smtModal{{ loop.index }}_{{ loop.index0 }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">{{ s.name }}</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ s.content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endfor %}

            {% if row.generated_test_content %}
            <div class="modal fade" id="testFileModal{{ loop.index }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">Generated Test: {{ row.contract_name }}.t.sol</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ row.generated_test_content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endif %}

            {% if row.log_content %}
            <div class="modal fade" id="logModal{{ loop.index }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Analysis Log: {{ row.contract_name }}</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ row.log_content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endif %}

            {% if row.test_log_content %}
            <div class="modal fade" id="foundryLogModal{{ loop.index }}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-dark text-white">
                            <h5 class="modal-title">Foundry Output: {{ row.contract_name }}</h5>
                            <button class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body"><pre>{{ row.test_log_content }}</pre></div>
                    </div>
                </div>
            </div>
            {% endif %}

        {% endfor %}

        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
        <script>
            $(document).ready(function(){
                $('#mainTable').DataTable({
                    "order": [[ 1, "desc" ]] 
                });
            });
        </script>
        </body>
        </html>
        """
        
        with open(os.path.join(self.output_dir, "SolidTG_Report.html"), "w", encoding="utf-8") as f:
            f.write(Template(template_str).render(data=self.data, timestamp=datetime.now()))
        print(f"HTML (Simplified) saved: {os.path.join(self.output_dir, 'SolidTG_Report.html')}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', '-o', type=str, required=True, help='Where to save the report')
    parser.add_argument('--sandbox_dir', '-s', type=str, required=True, help='Where the data files are')
    args = parser.parse_args()

    builder = ModernReportBuilder(args.output_dir, args.sandbox_dir)
    builder.scan()
    builder.generate_html()
    builder.generate_excel()