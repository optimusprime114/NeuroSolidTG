import argparse
import os
import re

import xlsxwriter


class html_report:

    def create_header(table):
        header_line = "No., Sourse dir, Sourse code, Links (smt2 logs reports) , Tests, Coverage, Time"
        header = header_line.split(",")
        table += "  <tr>\n"
        for column in header:
            table += "    <th>{0}</th>\n".format(column.strip())
        table += "  </tr>\n"
        return table


    def create_hyperlinnk_to_file(text):
        if not text:
            return "NaN"
        name = os.path.basename(text)
        if os.path.exists(text):
            return "<a href=\"{0}\">{1} </a>\n".format(text, name)
        else:
            return "NaN"

    def create_hyperlinnk_to_test_file(text):
        if not text:
            return "NaN"
        if os.path.exists(text):
            return "<a href=\"{0}\">{1} </a>\n".format(text, "test")
        else:
            return "NaN"

    def smt2_status(ll):
        if "smt2" not in ll:
            return "-"
        else:
            return ll[13]

    def smt2_number_of_lines(smt2file):
        if os.path.exists(smt2file):
            return len(open(smt2file).readlines())
        else:
            return "-"

    def link_to_log(p):
        name = os.path.dirname(p) + "/log.txt"
        return "<a href=\"{0}\">{1}</a>\n".format(name, "log")

    def get_z3_results(p):
        if "z3_error" in p:
            return "timeout"
        if len(p) > 15:
            if ('sat' in p[16] and 'unsat' not in p[16]):
                return 'sat'
            if ('unsat' in p[16]):
                return 'unsat'
        else:
            return "-"

    def parse_result_line(line):
        tmp = line.split(';')
        tmp_1 = tmp[0].split()
        out = ''
        if tmp_1[-2].isnumeric():
            if int(tmp_1[-2]) > 0:
               out += "<br/><font color=green>{}</font> ".format(tmp_1[-2] + " " + tmp_1[-1])
        tmp_2 = tmp[1].split()
        if tmp_2[-2].isnumeric():
            if int(tmp_2[-2]) > 0:
                out += "<br/><font color=red>{}</font> ".format(tmp[1])
        return out

    def parse_fun(line):
        tmp = line.split(';')
        tmp_1 = tmp[0].split()
        out = ''
        if tmp_1[-2].isnumeric():
            if int(tmp_1[-2]) > 0:
               out += tmp_1[-2] + " " + tmp_1[-1]
        tmp_2 = tmp[1].split()
        if tmp_2[-2].isnumeric():
            if int(tmp_2[-2]) > 0:
                out += tmp[1]
        return out

    @classmethod
    def get_extra_info_from_log(cls, dir):
        log = [f.path for f in os.scandir(dir) if f.is_file() and os.path.basename(f) == 'log.txt']
        out = ''
        if len(log) >= 1:
            what_to_check = ["Multiple queries are not supported",
                             "Assertion failed",
                             "Done with TG",
                             "array operation requires one sort parameter",
                             "ALL Branches are covered: DONE",
                             "FOUND", 'unrolling sat', 'unrolling unsat',
                             "index_cycle_chc :",
                             'RUST_BACKTRACE',
                             "# TESTS:", 'Multiple Calls Test']
            filein = open(log[0], "r", encoding='ISO-8859-1')
            lines = filein.readlines()
            for w in what_to_check:
                for line in lines:
                    if re.search(w, line):
                        out += "<br/>" + "<font color=8B008B>{}</font>\n".format(line)
                        break
        return out



    @classmethod
    def clear_benchmarkdir(self, dir, nonlinear):
        for n in nonlinear:
            tmp = dir + "/" + n + ".c"
            if os.path.isfile(tmp):
                # remove dir
                os.remove(tmp)


    @classmethod
    def get_tests_info(cls, dir):
        test_results = [f.path for f in os.scandir(dir) if f.is_file() and os.path.basename(f) == 'test_results.txt']
        out = ''
        if len(test_results) >= 1:
            what_to_check = ["No tests match",
                             "Unnamed return variable",
                             "Done with TG",
                             "array operation requires one sort parameter"]
            filein = open(test_results[0], "r", encoding='ISO-8859-1')
            lines = filein.readlines()
            for line in lines:
                if "Test result:" in line:
                    out += "<br/>" + cls.parse_result_line(line)
            for w in what_to_check:
                for line in lines:
                    if re.search(w, line):
                        out += "<br/>" + "<font color=8B008B>{}</font>\n".format(w)
                        break
            return out
        else:
            return "No info"


    @classmethod
    def get_number_of_test(cls, dir):
        test_results = [f.path for f in os.scandir(dir) if f.is_file() and os.path.basename(f) == 'test_results.txt']
        out = 0
        if len(test_results) >= 1:
            filein = open(test_results[0], "r", encoding='ISO-8859-1')
            lines = filein.readlines()
            for line in lines:
                if "Test result:" in line:
                    tmp = cls.parse_fun(line).split()
                    if len(tmp) > 1:
                        out += int(tmp[0])
            return out
        else:
            return 0


    @classmethod
    def get_number_of_line_in_original_sorse_file(cls, dir):
        sol_file = dir + "/" + os.path.basename(dir) + ".sol"
        if os.path.exists(sol_file):
            return len(open(sol_file, "r").readlines())
        else:
            return 0


    @classmethod
    def read_lcov_html_report(cls, file_name):
        file = open(file_name, "r")
        lines = file.readlines()
        brench_lines = []
        flag = False
        i = 0
        for line in lines:
            if flag:
                brench_lines.append(re.sub('<[^<]+?>', '', line))
                i += 1
            if 'Branches:' in line:
                brench_lines.append(re.sub('<[^<]+?>', '', line))
                flag = True
            if i == 3:
                break
        return '{}<br/>\nHit: {}<br/>\nTotal: {}<br/>\nCoverage: {}\n'.format(brench_lines[0], brench_lines[1],
                                                                              brench_lines[2], brench_lines[3])



    @classmethod
    def get_coverage_data(cls, dir):
        sub_dirs = [f.path for f in os.scandir(dir) if f.is_dir() and os.path.basename(f) in 'generated-coverage']
        if len(sub_dirs) != 1:
            return "<font color=\"red\">{}</font>\n".format('no data')
        else:
            report_dir = [f.path for f in os.scandir(sub_dirs[0]) if f.is_dir()]
            report_dir = [d for d in report_dir if os.path.basename(d)]
            if len(report_dir) != 1:
                return "<font color=\"red\">{}</font>\n".format('no report')
            else:
                file_name = report_dir[0] + '/src/' + os.path.basename(dir) +'.sol.gcov.html'
                out = "<a href=\"{0}\">{1} </a>\n".format(file_name, "coverage_c_file_TG") + '<br/>\n'
                out += html_report.read_lcov_html_report(file_name) + '<br/>'
                return out


    @classmethod
    def read_lcov_html_report_plane_text(cls, file_name):
        file = open(file_name, "r")
        lines = file.readlines()
        brench_lines = []
        flag = False
        i = 0
        for line in lines:
            if flag:
                brench_lines.append(re.sub('<[^<]+?>', '', line))
                i += 1
            if 'Branches:' in line:
                brench_lines.append(re.sub('<[^<]+?>', '', line))
                flag = True
            if i == 3:
                break
        return brench_lines



    @classmethod
    def get_coverage_data_plane_text(cls, dir):
        sub_dirs = [f.path for f in os.scandir(dir) if f.is_dir() and os.path.basename(f) in 'generated-coverage']
        if len(sub_dirs) != 1:
            return 'no data'
        else:
            report_dir = [f.path for f in os.scandir(sub_dirs[0]) if f.is_dir()]
            report_dir = [d for d in report_dir if os.path.basename(d)]
            if len(report_dir) != 1:
                return 'no report'
            else:
                file_name = report_dir[0] + '/src/' + os.path.basename(dir) +'.sol.gcov.html'
                out = html_report.read_lcov_html_report_plane_text(file_name)
                return out


    @classmethod
    def read_lcov_html_report_plane_text_function_number(cls, file_name):
        file = open(file_name, "r")
        lines = file.readlines()
        brench_lines = []
        flag = False
        i = 0

        for line in lines:
            if flag:
                brench_lines.append(re.sub('<[^<]+?>', '', line))
                i += 1
            if 'Functions:' in line:
                brench_lines.append(re.sub('<[^<]+?>', '', line))
                flag = True
            if i == 3:
                break
        return brench_lines


    @classmethod
    def get_function_number_plane_text(cls, dir):
        sub_dirs = [f.path for f in os.scandir(dir) if f.is_dir() and os.path.basename(f) in 'generated-coverage']
        if len(sub_dirs) != 1:
            return 'no data'
        else:
            report_dir = [f.path for f in os.scandir(sub_dirs[0]) if f.is_dir()]
            exclude = ['usr']
            report_dir = [d for d in report_dir if os.path.basename(d) not in exclude]
            if len(report_dir) != 1:
                return 'no report'
            else:
                file_name = report_dir[0] + '/src/' + os.path.basename(dir) +'.sol.gcov.html'
                out = html_report.read_lcov_html_report_plane_text_function_number(file_name)
                return out



    @classmethod
    def buildReport(self, dir):
        fileout = open("{}/1_html_report.html".format(dir), "w+")

        table = "<table border=\"1\" cellspacing=\"0\" cellpadding=\"4\">\n"
        table = html_report.create_header(table)

        i = 1
        subdirs = [f.path for f in os.scandir(dir) if f.is_dir() and os.path.basename(f)]
        out = []
        for s in subdirs:
            out += [(s, f.path) for f in os.scandir(s) if f.is_dir() and os.path.basename(f)]
        for o in sorted(out):
            (subd, line) = o
            print(line)
            table += "  <tr>\n"
            table += "    <td>{0}</td>\n".format(i)
            table += "    <td>{0}<br/>\n".format(
                html_report.create_hyperlinnk_to_file(subd))
            table += "    <td>{0}<br/>\n".format(
                html_report.create_hyperlinnk_to_file(line + '/' + os.path.basename(line) + '.sol'))
            table += "    <td>{0}<br/>{1}<br/>{2}<br/>{3}<br/>{4}<br/></td>\n".format(html_report.get_smt2_file(line),
                                                            html_report.get_log_file(line, "log.txt"),
                                                            html_report.get_log_file(line, "log_encoding.txt"),
                                                            html_report.get_extra_info_from_log(line),
                                                            html_report.get_log_file(line, "imag.png"))
            table += "    <td>{0}<br/>{1}<br/>{2}</br>{3}</td>\n".format(html_report.create_hyperlinnk_to_test_file(line + '/' + os.path.basename(line) + '.t.sol'),
                                                         html_report.get_log_file(line, "test_results.txt"),
                                                        html_report.create_hyperlinnk_to_file(line + '/testgen.txt'),
                                                        html_report.get_tests_info(line))
            table += "    <td>{0}</td>\n".format(html_report.get_coverage_data(line))
            table += "    <td>{0}</td>\n".format(str(html_report.get_time_consumed(line)) + ' seconds')
            table += "  </tr>\n"
            i += 1
        table += "</table>"
        # table = table.replace("../{}".format(dir), ".")
        #table = table.replace(dir, ".")
        fileout.writelines(table)
        fileout.close()



    @classmethod
    def get_smt2_file(cls, dir):
        smt2files = [f.path for f in os.scandir(dir) if f.is_file() and os.path.splitext(f)[1] == '.smt2']
        if len(smt2files) >= 1:
            out = ""
            for f in sorted(smt2files):
                if "wo_adt" not in f:
                    out += "<font color=\"black\">[original smt]<br/> {}</font><br/>\n".format(html_report.create_hyperlinnk_to_file(f))
                else:
                    out += "<font color=\"black\">[adt free smt]<br/> {}</font><br/>\n".format(
                        html_report.create_hyperlinnk_to_file(f))
            return out
        else:
            return "<font color=\"red\">{}</font>\n".format('no smt')

    @classmethod
    def get_log_file(cls, dir, log_file_name):
        log = [f.path for f in os.scandir(dir) if f.is_file() and os.path.basename(f) == log_file_name]
        if len(log) >= 1:
            return html_report.create_hyperlinnk_to_file(log[0])
        else:
            return "<font color=\"red\">{}</font>\n".format('no log')


    @classmethod
    def get_time_consumed(cls, dir):
        log = [f.path for f in os.scandir(dir) if f.is_file() and os.path.basename(f) == 'log.txt']
        if len(log) >= 1:
            with open(log[0], 'rb') as f:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
                last_line = f.readline().decode()
                time_con = last_line.split()
                if len(time_con) > 3 and ("total time" in last_line):
                    return "%8.2f" % (float(time_con[2]))
                else:
                    "<font color=\"red\">{}</font>\n".format('no available')
        else:
            return "<font color=\"red\">{}</font>\n".format('no available')



    def is_nonlinear(name):
        filein = open(name, "r", encoding='ISO-8859-1')
        lines = filein.readlines()
        for l in lines:
            if "Nonlinear CHC is currently unsupported" in l:
                return False
        return True


    @classmethod
    def build_excel_report(self, dir):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(dir + '/1_report.xlsx')
        worksheet = workbook.add_worksheet()

        expenses = [['dir', 'filename', 'coverage',  'time', 'hit', 'total', '#fun_hit', '#fun_total', '# tests', '# lines']]
        subdirs = [f.path for f in os.scandir(dir) if f.is_dir() and os.path.basename(f)]
        out = []
        for s in subdirs:
            out += [(s, f.path) for f in os.scandir(s) if f.is_dir() and os.path.basename(f)]
        for o in sorted(out):
            (subd, line) = o
            dir_name = os.path.basename(subd)
            file_name = os.path.basename(line) + '.sol'
            raw_data = html_report.get_coverage_data_plane_text(line)
            coverage = ""
            if raw_data != "no data" and raw_data != 'no report':
                raw_data = [r.strip("\n") for r in raw_data]
                coverage = raw_data[1].strip("%")
                print(raw_data)
                hit = float(raw_data[3])
                total = float(raw_data[2])
            else:
                coverage = 0
                hit = ''
                total = ''

            fun_number = html_report.get_function_number_plane_text(line)
            if not isinstance(fun_number, (bool)) and fun_number != "no data" and raw_data != 'no report':
                fun_number = [r.strip("\n") for r in fun_number]
                test1 = fun_number[1]
                test2 = fun_number[2]
            else:
                coverage_TG = 0
                test1 = ''
                test2 = ''

            time = html_report.get_time_consumed(line)
            number_of_tests = html_report.get_number_of_test(line)
            number_of_line = html_report.get_number_of_line_in_original_sorse_file(line)
            expenses.append([dir_name, file_name, coverage, time, hit, total, test1, test2, number_of_tests, number_of_line])

        row = 0
        col = 0

        for dir_name, file_name, coverage, time, hit, total, fun_number_hit, fun_number_total, number_of_tests, number_of_line in expenses:
            worksheet.write(row, col, dir_name)
            worksheet.write(row, col + 1, file_name)
            worksheet.write(row, col + 2, coverage)
            worksheet.write(row, col + 3, time)
            worksheet.write(row, col + 4, hit)
            worksheet.write(row, col + 5, total)
            worksheet.write(row, col + 6, fun_number_hit)
            worksheet.write(row, col + 7, fun_number_total)
            worksheet.write(row, col + 8, number_of_tests)
            worksheet.write(row, col + 9, number_of_line)
            row += 1

        workbook.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='python script for Report Builder')
    insourse = ['-i', '--input_dir']
    kwsourse = {'type': str, 'help': 'dir: where TG run is located'}
    parser.add_argument(*insourse, **kwsourse)
    args = parser.parse_args()

    if args.input_dir is not None:
        if os.path.isdir(args.input_dir):
            dir = args.input_dir
            print('report dir set to {}'.format(dir))
    else:
        dir = "/Users/ilyazlatkin/CLionProjects/blockchain_exp/hello_foundry/testgen_output"
        dir = "/Users/ilyazlatkin/Downloads/testgen_output"
        #dir = "/Users/ilyazlatkin/PycharmProjects/results/blockchain/regression_sanity_2/testgen_output"

    html_report.buildReport(dir)
    html_report.build_excel_report(dir)

