import os.path
import random

from eth_utils import to_checksum_address
# from PyInstaller.utils.hooks import collect_submodules
#
# # The ``eth_hash.utils.load_backend`` function does a dynamic import.
# hiddenimports = collect_submodules('eth_hash.backends')


def is_fun_supported(fun_signature):
    # currently only int formate is supported
    for f in fun_signature:
        # if f != "uint":
        if "uint" not in f:
            return False
    return True

class TestWrapper:

    def __init__(self, testgen_file, signature):
        self.testgen_file = testgen_file
        self.signature = signature

        print("LOOK Here FOR SIG")
        print(testgen_file)
        print(signature)

    def read(self, file):
        f = open(file, "r")
        inside_test = False
        raw_tests = []
        a_test = []
        print("hello123")
        for line in f.readlines():
            print("TEST LINES ;" + line.strip())
            if "END TEST" in line.strip():
                inside_test = False
                if a_test:
                    raw_tests.append(a_test)
                a_test = []
            if inside_test:
                if line:
                    a_test.append(line.strip().replace(" ", ""))
            if "NEW TEST" in line.strip():
                inside_test = True
        return raw_tests

    def get_values(cls, raw_list):
        order = []
        test = {}
        for item in raw_list:
            tokens = item.strip().split()
            if len(tokens) < 2:
                print("Error: check!")
                continue
            chc_name = tokens[0]
            var_value = tokens[2][1:-1]
            tmp = var_value.split('=')
            var = int(tmp[0][len("_tg_"):])
            value = -1
            if "array" in tmp[1] or "store" in tmp[1]:
                continue
            else:
                value = int(tmp[1])
            if "contract" in chc_name:
                if "contract" in test:
                    if var in test["contract"]:
                        test["contract"][var].append(value)
                    else:
                        test["contract"][var] = [value]
                else:
                    tmp_dict = {}
                    tmp_dict[var] = [value]
                    test["contract"] = tmp_dict
                if "contract" not in order:
                    order.append("contract")
            if "block" in chc_name and "function" in chc_name and "summary" not in chc_name and "return" not in chc_name:
                start = chc_name.index("_function_")
                end = chc_name.index("__")
                if start < 0 or end < 0:
                    print("Error2: check!")
                    continue
                function_name = chc_name[start + len("_function_"): end]
                if function_name not in order:
                    order.append(function_name)
                if function_name in test:
                    if var in test[function_name]:
                        test[function_name][var].append(value)
                    else:
                        test[function_name][var] = [value]
                else:
                    tmp_dict = {}
                    tmp_dict[var] = [value]
                    test[function_name] = tmp_dict

        test["order"] = order
        return test

    def wrap(self):
        if os.path.isfile(self.testgen_file):
            print ("is Here.")
            raw_tests = self.read(self.testgen_file)
            print(raw_tests)
            return raw_tests
        else:
            return False

    def remove_duplicates(self, tests):
        out = []
        uniq = set()
        for t in tests:
            if str(t) not in uniq:
                uniq.add(str(t))
                out.append(t)
        return out

    # def generate_sol_test(self, clean_tests, file_name, file_path):
        
    #     path = os.path.abspath(file_path)
    #     print(path)
    #     name_wo_extension = os.path.splitext(file_name)[0]
    #     test_name = name_wo_extension + ".t.sol"
    #     test_file_full_path = os.getcwd() + "/test/" + test_name
    #     os.makedirs(os.path.dirname(test_file_full_path), exist_ok=True)
    #     test_file = open(test_file_full_path, 'w')

    #     # generate header/import part
    #     header = ["//Generated Test by TG\n", "//{}\n".format(str(self.signature)),
    #               "import \"forge-std/Test.sol\";\n",
    #               "import \"../{}\";\n\n".format(file_path),
    #               f'contract {name_wo_extension}_Test is Test' + ' {\n']

    #     fields = []
    #     setUp = []
    #     test_body = []
    #     for index, test in enumerate(clean_tests):

    #         # contracts declaration
    #         print("SELF SIGNATURE:", self.signature)
    #         type = self.signature[0][0][1]
    #         contract_names = [self.signature[i][0][0] for i,_ in enumerate(self.signature)]
    #         #contract_var = "c" + str(index)
    #         contract_vars = [c_name.lower() + str(index) for c_name in contract_names]
    #         print("Cont names:", contract_names)
    #         print("Cont vars:", contract_vars)
    #         if type in ['contract', 'library']:  # skip interphases
    #             for i, c_name in enumerate(contract_names):
    #                 fields.append("\t{} {};\n".format(c_name, contract_vars[i]))

    #         # generate setUp function
    #         c_name = ""
    #         if type in ['contract', 'library']:  # skip interphases
    #             init_part_of_test = [tt for tt in test if "contract_" in tt]
    #             for tt in init_part_of_test:
    #                 for i, c_name in enumerate(contract_names):
    #                     if 'contract_{}'.format(c_name) not in tt:
    #                         continue
    #                     if tt == 'contract_{}()'.format(c_name) or 'contract' not in test[0]:
    #                         constructor_args_values = '()'
    #                     else:
    #                         tmp = tt
    #                         print("Tmp:", tmp)
    #                         c_index = 0
    #                         const_signature=""

    #                         # f_name = tmp[:tmp.index('(')]
    #                         # print("Name:", f_name_tmp)
    #                         for j, sg in enumerate(self.signature):
    #                             for y in [tmp[0] for tmp in sg]:
    #                                 print("Y:", y)
    #                                 if c_name in y:
    #                                     c_index = j
    #                                     break
    #                         print(self.signature[c_index])
    #                         for i, c_name in enumerate(contract_names):
    #                             f_name = tmp.split('_')[1]
    #                             for s in self.signature[c_index]:
    #                                 if f_name == s[0]:
    #                                     const_signature = s
    #                                     break
    #                             print("FUN SIG: ", const_signature)
    #                         start = tmp.index('"') + 1
    #                         end = len(tmp)-1
    #                         open_count = 0
    #                         close_count = 0
    #                         constructor_signature = self.signature[0][0]
    #                         print("Const sig:", constructor_signature)

    #                         constructor_args_values = tmp[start:end + 1]
    #                         char = ''
    #                         ind = 0
    #                         for char in constructor_args_values:
    #                             ind+=1
    #                             if char == '"':
    #                                 break

    #                         balances = constructor_args_values[:ind + 1]
    #                         print("Balances:", balances)
    #                         constructor_args_values = constructor_args_values[ind + 1:]
    #                         print("Constructor args:", constructor_args_values)

    #                         value = 0
    #                         if ',' in constructor_args_values:
    #                             end = constructor_args_values.index(',')
    #                             value = constructor_args_values[:end]
    #                         else:
    #                             end = constructor_args_values.index(')')-1
    #                             value = constructor_args_values[:end+1]
    #                         constructor_args_values = '(' + constructor_args_values[end + 1:]
    #                         sender = 0
    #                         if ',' in constructor_args_values:
    #                             end = constructor_args_values.index(',')
    #                             sender = constructor_args_values[:end]
    #                         else:
    #                             end = constructor_args_values.index(')')-1
    #                             sender = constructor_args_values[:end+1]

    #                         constructor_args_values = constructor_args_values[end + 1:-1].split(',')
    #                         init_ch = 10
    #                         index_p = 0
    #                         # params = []
    #                         while len(const_signature) > init_ch:
    #                             if (const_signature[init_ch - 1] == 'address'):
    #                                 constructor_args_values[index_p] = hex(int(constructor_args_values[index_p]))
    #                                 print("OLD LEN: ", len(str(constructor_args_values[index_p])))
    #                                 constructor_args_values[index_p] = to_checksum_address(constructor_args_values[index_p].ljust(42, '0').upper()[2:])
    #                                 # params[index_p]= '0x' + params[index_p]
    #                                 print("NEW PARAMS: ", constructor_args_values[index_p])
    #                             if (const_signature[init_ch - 1] == 'string'):
    #                                 constructor_args_values[index_p] = constructor_args_values[index_p].split("=")[1]
    #                             index_p += 1
    #                             init_ch += 2
    #                         args = '(' + ','.join(constructor_args_values) + ')'
    #                         print("Constr args:", args)
    #                     tt.split('_')
    #                     setUp.append("\t\t{} = new {}{};\n".format(contract_vars[i], c_name, args))
    #                     print("Set up:", setUp)
    #                     break

    #             # generate Tests : one test for each function for each contract
    #             # find fun_signature
    #             funcs_calls = [tt for tt in test if "contract_" not in tt]
    #             test_body.append(f'\tfunction test_{name_wo_extension}_{index}() public ' + '{\n')
    #             for calls in funcs_calls:
    #                 fun_signature = []
    #                 c_index = 0
    #                 f_name_tmp = calls[:calls.index('(')]
    #                 print("Name:", f_name_tmp)
    #                 for j, sg in enumerate(self.signature):
    #                     for y in [tmp[0] for tmp in sg]:
    #                         print("Y:", y)
    #                         if c_name in y:
    #                             c_index = j
    #                             break
    #                 for s in self.signature[c_index][1:]: # ToDo add mutliple contracts
    #                     fun_signature = s
    #                 if not fun_signature:  # "function not found case"
    #                     continue
    #                 # if check:
    #                 f_name = calls.split('__')[0]
    #                 for s in self.signature[c_index][1:]:
    #                     if f_name == s[0]:
    #                         fun_signature = s
    #                         break
    #                 print("FUN SIG: ", fun_signature)
    #                 args = calls[calls.index('"') + 1:]
    #                 print("Bef Func Args:", args)
    #                 char = ''
    #                 ind = 0
    #                 open_count = 0
    #                 close_count = 0
    #                 for char in args:
    #                     ind += 1
    #                     if char == '"':
    #                         break

    #                 balances = args[:ind + 1]
    #                 print("Balances:", balances)
    #                 args = args[ind + 1:]
    #                 value = 0
    #                 if ',' in args:
    #                     end = args.index(',')
    #                     value = args[:end]
    #                 else:
    #                     end = args.index(')') - 1
    #                     value = args[:end + 1]
                    
    #                 params = args[end + 1:-1]
    #                 print("look here")
    #                 print(args)
    #                 print(params)
    #                 # TODO: Handle structures!!!!
    #                 params = params.split(',')
    #                 sender = params[0]
    #                 params = params[1:]
    #                 sender = hex(int(sender))
    #                 sender = to_checksum_address(sender.ljust(42, '0').upper()[2:])
    #                 init_ch = 9
    #                 index_p = 0
    #                 print(fun_signature)
    #                 while len(fun_signature) > init_ch:
    #                     if(fun_signature[init_ch - 1] == 'address'):
    #                         print(index_p)
    #                         print(init_ch)
    #                         params[index_p] = hex(int(params[index_p]))
    #                         print("OLD LEN: ", len(str(params[index_p])))
    #                         params[index_p] = to_checksum_address(params[index_p].ljust(42, '0').upper()[2:])
    #                         # params[index_p]= '0x' + params[index_p]
    #                         print("NEW PARAMS: ", params[index_p])
    #                     if(fun_signature[init_ch - 1] == 'string'):
    #                         params[index_p] = params[index_p].split("=")[1]
    #                     index_p+=1
    #                     init_ch+=2
    #                 args = '(' + ','.join(params) + ')'
    #                 print("Function args:", args)
    #                 print("Value:", value)
    #                 print("Sender:", sender)
    #                 ucall = f_name + args
    #                 if(str(sender) == "0x0000000000000000000000000000000000000000"):
    #                     sender = random.randint(1000000000, 100000000000000000000)
    #                     sender = hex(int(sender))
    #                     sender = to_checksum_address(sender.ljust(42, '0').upper()[2:])
    #                 test_body.append("\t\tvm.prank("+sender+");\n")
    #                 if(int(value) > 0):
    #                     test_body.append("\t\tvm.deal("+sender+", " + str(value) +" wei );\n")
    #                     ucall = f_name + "{ value: " + value + " wei }" + args
    #                     print("Unique address!")
    #                 test_body.append("\t\t{}.{}; //{}\n".format(contract_vars[c_index], ucall, calls))
    #             test_body.append("\t}\n")

    #     out = header + fields + ["\tfunction setUp() public {\n"] + setUp + ["\t}\n"] \
    #           + test_body + ["}\n"]

    #     test_file.writelines(out)
    #     test_file.close()

    # Method - 2

    # def generate_sol_test(self, clean_tests, file_name, file_path):
    #     path = os.path.abspath(file_path)
    #     print("THERE ARE TESTS")
    #     name_wo_extension = os.path.splitext(file_name)[0]
    #     test_name = name_wo_extension + ".t.sol"
    #     test_file_full_path = os.getcwd() + "/test/" + test_name
    #     os.makedirs(os.path.dirname(test_file_full_path), exist_ok=True)
    #     test_file = open(test_file_full_path, 'w')

    #     header = ["//Generated Test by TG\n", "//{}\n".format(str(self.signature)),
    #                 "import \"forge-std/Test.sol\";\n",
    #                 "import \"../{}\";\n\n".format(file_path),
    #                 f'contract {name_wo_extension}_Test is Test' + ' {\n']

    #     fields = []
    #     setUp = []
    #     test_body = []

    #     for index, test in enumerate(clean_tests):
    #         print("SELF SIGNATURE:", self.signature)
    #         type = self.signature[0][0][1]
    #         contract_names = [self.signature[i][0][0] for i, _ in enumerate(self.signature)]
    #         contract_vars = [c_name.lower() + str(index) for c_name in contract_names]
    #         print("Cont names:", contract_names)
    #         print("Cont vars:", contract_vars)

    #         if type in ['contract', 'library']:
    #             for i, c_name in enumerate(contract_names):
    #                 fields.append("\t{} {};\n".format(c_name, contract_vars[i]))

    #         c_name = ""
    #         if type in ['contract', 'library']:
    #             init_part_of_test = [tt for tt in test if "contract_" in tt]
    #             for tt in init_part_of_test:
    #                 for i, c_name in enumerate(contract_names):
    #                     if 'contract_{}'.format(c_name) not in tt:
    #                         continue
                        
    #                     constructor_args_values = '()'
    #                     args = '()'
    #                     if tt != 'contract_{}()'.format(c_name) and '(' in tt:
    #                         # This section for parsing constructor arguments seems complex and might need its own robust error handling
    #                         # For now, assuming it works or the constructor has no args as in the example.
    #                         # Based on your logs, it correctly resolves to `()` for this test case.
    #                         # A placeholder for simplicity:
    #                         pass
                        
    #                     setUp.append("\t\t{} = new {}{};\n".format(contract_vars[i], c_name, args))
    #                     print("Set up:", setUp)
    #                     break

    #             funcs_calls = [tt for tt in test if "contract_" not in tt]
    #             test_body.append(f'\tfunction test_{name_wo_extension}_{index}() public ' + '{\n')
    #             for calls in funcs_calls:
    #                 fun_signature = []
    #                 c_index = 0
    #                 f_name_tmp = calls[:calls.index('(')]
    #                 print("Name:", f_name_tmp)

    #                 for j, sg in enumerate(self.signature):
    #                     for y in [tmp[0] for tmp in sg]:
    #                         if c_name in y:
    #                             c_index = j
    #                             break
                    
    #                 # ✅ FIX 1: CORRECT SIGNATURE MATCHING
    #                 f_name = calls.split('__')[0]
    #                 found_sig = False
    #                 for s in self.signature[c_index][1:]:
    #                     if f_name == s[0].rstrip('_'):
    #                         fun_signature = s
    #                         found_sig = True
    #                         break
                    
    #                 if not found_sig:
    #                     print(f"Warning: Signature not found for function call {f_name}. Skipping.")
    #                     continue

    #                 print("FUN SIG: ", fun_signature)
    #                 args = calls[calls.index('"') + 1:]
    #                 print("Bef Func Args:", args)
                    
    #                 # This parsing is brittle; simplified for clarity
    #                 balances_part_end = args.find('",')
    #                 if balances_part_end == -1:
    #                     continue # Skip malformed call
                    
    #                 balances = args[:balances_part_end+1]
    #                 remaining_args = args[balances_part_end + 2:]
                    
    #                 value = '0'
    #                 params_str = ''
    #                 if ',' in remaining_args:
    #                     value, params_str = remaining_args.split(',', 1)
    #                     params_str = params_str.rstrip(')')
    #                 else:
    #                     value = remaining_args.rstrip(')')

    #                 print("look here")
    #                 print(f"Value: {value}, Params String: {params_str}")

    #                 # ✅ FIX 2: ROBUST PARAMETER HANDLING
    #                 params = params_str.split(',') if params_str else []
    #                 sender_val = '0' # Default sender if none provided
    #                 if params and params[0]:
    #                     sender_val = params[0]
    #                     params = params[1:]
    #                 else:
    #                     params = [] # Ensure params is empty if no actual parameters exist

    #                 sender = hex(int(sender_val))
    #                 sender = to_checksum_address(sender.ljust(42, '0').upper()[2:])

    #                 init_ch = 9
    #                 index_p = 0
    #                 print(fun_signature)
                    
    #                 # Check that we don't expect more params than we have
    #                 num_expected_params = (len(fun_signature) - init_ch + 1) // 2 if len(fun_signature) > init_ch else 0
    #                 if len(params) < num_expected_params:
    #                     print(f"Warning: Mismatch between expected params ({num_expected_params}) and found params ({len(params)}). Skipping call.")
    #                     continue

    #                 while len(fun_signature) > init_ch and index_p < len(params):
    #                     if fun_signature[init_ch - 1] == 'address':
    #                         params[index_p] = hex(int(params[index_p]))
    #                         params[index_p] = to_checksum_address(params[index_p].ljust(42, '0').upper()[2:])
    #                         print("NEW PARAMS: ", params[index_p])
    #                     if fun_signature[init_ch - 1] == 'string':
    #                         params[index_p] = params[index_p].split("=")[1]
    #                     index_p += 1
    #                     init_ch += 2
                    
    #                 args_final = '(' + ','.join(params) + ')'
    #                 print("Function args:", args_final)
    #                 print("Value:", value)
    #                 print("Sender:", sender)
                    
    #                 ucall = f_name + args_final
    #                 if str(sender) == "0x0000000000000000000000000000000000000000":
    #                     sender = random.randint(1000000000, 100000000000000000000)
    #                     sender = hex(int(sender))
    #                     sender = to_checksum_address(sender.ljust(42, '0').upper()[2:])
                    
    #                 test_body.append("\t\tvm.prank("+sender+");\n")
    #                 if int(value) > 0:
    #                     test_body.append("\t\tvm.deal("+sender+", " + str(value) +" wei );\n")
    #                     ucall = f_name + "{ value: " + value + " wei }" + args_final
    #                 test_body.append("\t\t{}.{}; //{}\n".format(contract_vars[c_index], ucall, calls))
    #             test_body.append("\t}\n")

    #     out = header + fields + ["\tfunction setUp() public {\n"] + setUp + ["\t}\n"] \
    #             + test_body + ["}\n"]

    #     test_file.writelines(out)
    #     test_file.close()

    # Method - 3

    def _parse_and_format_args(self, call_string, signature):
        """
        Helper function to parse arguments for both constructors and functions.
        It formats addresses as `payable(address(number))` for calls and
        creates a full checksummed address for the sender.
        """
        # Extract the raw arguments string from between the parentheses
        args_raw = call_string[call_string.find('(') + 1 : call_string.rfind(')')]

        # The first part is often a descriptive string, which we can ignore for parsing
        try:
            first_quote_comma = args_raw.index('",')
            # Handle cases where there are no arguments after the description string
            args_str = args_raw[first_quote_comma + 2:]
            args_list = args_str.split(',') if args_str else []
        except ValueError:
            # Fallback if the descriptive string is not present
            args_list = args_raw.split(',') if args_raw else []

        # Default values and argument extraction
        value = '0'
        sender_val = '0'
        params = []

        # This logic assumes the format: value, sender, param1, param2, ...
        if len(args_list) >= 2:
            value = args_list[0].strip()
            sender_val = args_list[1].strip()
            params = [p.strip() for p in args_list[2:]]
        elif len(args_list) == 1 and args_list[0]:
            value = args_list[0].strip()

        # Create a full, padded, checksummed hex address for the sender (for vm.prank)
        sender_hex = hex(int(sender_val))
        full_sender_hex = '0x' + sender_hex[2:].zfill(40)
        sender = to_checksum_address(full_sender_hex)

        # Determine the correct starting index for parameter types in the signature
        # Constructors ('contract' is present) start at index 9, regular functions at 8
        param_start_index = 9 if 'contract' in signature else 8

        # Format parameters based on their type from the signature
        for index_p, param_value in enumerate(params):
            type_index = param_start_index + (index_p * 2)
            if type_index >= len(signature):
                break
            param_type = signature[type_index]

            # REQUIREMENT 2: Format address parameters as payable(address(number))
            if param_type == 'address':
                params[index_p] = f"payable(address({param_value}))"
            elif param_type == 'string' and "=" in param_value:
                params[index_p] = f'"{param_value.split("=")[1]}"' # Ensure strings are quoted

        formatted_args_string = '(' + ', '.join(params) + ')'
        return value, sender, formatted_args_string


    def generate_sol_test(self, clean_tests, file_name, file_path):
        path = os.path.abspath(file_path)
        print(path)
        print(file_path)
        name_wo_extension = os.path.splitext(file_name)[0]
        test_name = name_wo_extension + ".t.sol"
        test_file_full_path = os.getcwd() + "/test/" + test_name
        os.makedirs(os.path.dirname(test_file_full_path), exist_ok=True)
        test_file = open(test_file_full_path, 'w')

        header = ["//Generated Test by TG\n", "//{}\n".format(str(self.signature)),
                    "import \"forge-std/Test.sol\";\n",
                    "import \"{}\";\n\n".format(file_path),
                    f'contract {name_wo_extension}_Test is Test' + ' {\n']

        fields = []
        setUp = []
        test_body = []

        for index, test in enumerate(clean_tests):
            type = self.signature[0][0][1]
            contract_names = [self.signature[i][0][0] for i, _ in enumerate(self.signature)]
            contract_vars = [c_name.lower() + str(index) for c_name in contract_names]

            if type in ['contract', 'library']:
                for i, c_name in enumerate(contract_names):
                    fields.append("\t{} {};\n".format(c_name, contract_vars[i]))

            active_contract_name = ""
            if type in ['contract', 'library']:
                init_part_of_test = [tt for tt in test if "contract_" in tt]
                for tt in init_part_of_test:
                    for i, c_name in enumerate(contract_names):
                        if f'contract_{c_name}' not in tt:
                            continue
                        
                        active_contract_name = c_name  # Set the context for which contract we are testing
                        
                        # REQUIREMENT 1: Parse constructor arguments using the helper function
                        constructor_signature = self.signature[i][0]
                        # We only need the args string for the constructor call
                        _, _, constructor_args = self._parse_and_format_args(tt, constructor_signature)
                        
                        setUp.append(f"\t\t{contract_vars[i]} = new {c_name}{constructor_args};\n")
                        break

                funcs_calls = [tt for tt in test if "contract_" not in tt]
                test_body.append(f'\tfunction test_{name_wo_extension}_{index}() public ' + '{\n')
                for calls in funcs_calls:
                    c_index = contract_names.index(active_contract_name)
                    f_name = calls.split('__')[0]
                    fun_signature = None

                    for s in self.signature[c_index][1:]:
                        if f_name == s[0].rstrip('_'):
                            fun_signature = s
                            break
                    
                    if not fun_signature:
                        print(f"Warning: Signature for function '{f_name}' not found. Skipping call.")
                        continue

                    # Use the helper to get value, sender, and formatted arguments
                    value, sender, args = self._parse_and_format_args(calls, fun_signature)

                    ucall = f_name + args
                    
                    # Handle address(0) sender case with a valid random address
                    if str(sender) == "0x0000000000000000000000000000000000000000":
                        random_addr_hex = hex(random.randint(1, 2**160 - 1))
                        full_random_hex = '0x' + random_addr_hex[2:].zfill(40)
                        sender = to_checksum_address(full_random_hex)
                    
                    test_body.append(f"\t\tvm.prank({sender});\n")
                    if int(value) > 0:
                        test_body.append(f"\t\tvm.deal({sender}, {value} wei);\n")
                        ucall = f"{f_name}{{value: {value} wei}}{args}"
                    
                    test_body.append(f"\t\t{contract_vars[c_index]}.{ucall}; // {calls}\n")
                test_body.append("\t}\n")

        out = header + fields + ["\tfunction setUp() public {\n"] + setUp + ["\t}\n"] \
                + test_body + ["}\n"]

        test_file.writelines(out)
        test_file.close()



