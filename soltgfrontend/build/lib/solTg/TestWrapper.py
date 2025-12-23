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

    def read(self, file):
        f = open(file, "r")
        inside_test = False
        raw_tests = []
        a_test = []
        for line in f.readlines():
            if "END TEST" in line:
                inside_test = False
                if a_test:
                    raw_tests.append(a_test)
                a_test = []
            if inside_test:
                if line:
                    a_test.append(line.strip())
            if "NEW TEST" in line:
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

    def generate_sol_test(self, clean_tests, file_name, file_path):
        path = os.path.abspath(file_path)
        print(path)
        name_wo_extension = os.path.splitext(file_name)[0]
        test_name = name_wo_extension + ".t.sol"
        test_file_full_path = os.getcwd() + "/test/" + test_name
        os.makedirs(os.path.dirname(test_file_full_path), exist_ok=True)
        test_file = open(test_file_full_path, 'w')

        # generate header/import part
        header = ["//Generated Test by TG\n", "//{}\n".format(str(self.signature)),
                  "import \"forge-std/Test.sol\";\n",
                  "import \"../{}\";\n\n".format(file_path),
                  f'contract {name_wo_extension}_Test is Test' + ' {\n']

        fields = []
        setUp = []
        test_body = []
        for index, test in enumerate(clean_tests):

            # contracts declaration
            print("SELF SIGNATURE:", self.signature)
            type = self.signature[0][0][1]
            contract_names = [self.signature[i][0][0] for i,_ in enumerate(self.signature)]
            #contract_var = "c" + str(index)
            contract_vars = [c_name.lower() + str(index) for c_name in contract_names]
            print("Cont names:", contract_names)
            print("Cont vars:", contract_vars)
            if type in ['contract', 'library']:  # skip interphases
                for i, c_name in enumerate(contract_names):
                    fields.append("\t{} {};\n".format(c_name, contract_vars[i]))

            # generate setUp function
            c_name = ""
            if type in ['contract', 'library']:  # skip interphases
                init_part_of_test = [tt for tt in test if "contract_" in tt]
                for tt in init_part_of_test:
                    for i, c_name in enumerate(contract_names):
                        if 'contract_{}'.format(c_name) not in tt:
                            continue
                        if tt == 'contract_{}()'.format(c_name) or 'contract' not in test[0]:
                            constructor_args_values = '()'
                        else:
                            tmp = tt
                            print("Tmp:", tmp)
                            c_index = 0
                            const_signature=""

                            # f_name = tmp[:tmp.index('(')]
                            # print("Name:", f_name_tmp)
                            for j, sg in enumerate(self.signature):
                                for y in [tmp[0] for tmp in sg]:
                                    print("Y:", y)
                                    if c_name in y:
                                        c_index = j
                                        break
                            print(self.signature[c_index])
                            for i, c_name in enumerate(contract_names):
                                f_name = tmp.split('_')[1]
                                for s in self.signature[c_index]:
                                    if f_name == s[0]:
                                        const_signature = s
                                        break
                                print("FUN SIG: ", const_signature)
                            start = tmp.index('"') + 1
                            end = len(tmp)-1
                            open_count = 0
                            close_count = 0
                            constructor_signature = self.signature[0][0]
                            print("Const sig:", constructor_signature)

                            constructor_args_values = tmp[start:end + 1]
                            char = ''
                            ind = 0
                            for char in constructor_args_values:
                                ind+=1
                                if char == '"':
                                    break

                            balances = constructor_args_values[:ind + 1]
                            print("Balances:", balances)
                            constructor_args_values = constructor_args_values[ind + 1:]
                            print("Constructor args:", constructor_args_values)

                            value = 0
                            if ',' in constructor_args_values:
                                end = constructor_args_values.index(',')
                                value = constructor_args_values[:end]
                            else:
                                end = constructor_args_values.index(')')-1
                                value = constructor_args_values[:end+1]
                            constructor_args_values = '(' + constructor_args_values[end + 1:]
                            sender = 0
                            if ',' in constructor_args_values:
                                end = constructor_args_values.index(',')
                                sender = constructor_args_values[:end]
                            else:
                                end = constructor_args_values.index(')')-1
                                sender = constructor_args_values[:end+1]

                            constructor_args_values = constructor_args_values[end + 1:-1].split(',')
                            init_ch = 10
                            index_p = 0
                            # params = []
                            while len(const_signature) > init_ch:
                                if (const_signature[init_ch - 1] == 'address'):
                                    constructor_args_values[index_p] = hex(int(constructor_args_values[index_p]))
                                    print("OLD LEN: ", len(str(constructor_args_values[index_p])))
                                    constructor_args_values[index_p] = to_checksum_address(constructor_args_values[index_p].ljust(42, '0').upper()[2:])
                                    # params[index_p]= '0x' + params[index_p]
                                    print("NEW PARAMS: ", constructor_args_values[index_p])
                                if (const_signature[init_ch - 1] == 'string'):
                                    constructor_args_values[index_p] = constructor_args_values[index_p].split("=")[1]
                                index_p += 1
                                init_ch += 2
                            args = '(' + ','.join(constructor_args_values) + ')'
                            print("Constr args:", args)
                        tt.split('_')
                        setUp.append("\t\t{} = new {}{};\n".format(contract_vars[i], c_name, args))
                        print("Set up:", setUp)
                        break

                # generate Tests : one test for each function for each contract
                # find fun_signature
                funcs_calls = [tt for tt in test if "contract_" not in tt]
                test_body.append(f'\tfunction test_{name_wo_extension}_{index}() public ' + '{\n')
                for calls in funcs_calls:
                    fun_signature = []
                    c_index = 0
                    f_name_tmp = calls[:calls.index('(')]
                    print("Name:", f_name_tmp)
                    for j, sg in enumerate(self.signature):
                        for y in [tmp[0] for tmp in sg]:
                            print("Y:", y)
                            if c_name in y:
                                c_index = j
                                break
                    for s in self.signature[c_index][1:]: # ToDo add mutliple contracts
                        fun_signature = s
                    if not fun_signature:  # "function not found case"
                        continue
                    # if check:
                    f_name = calls.split('__')[0]
                    for s in self.signature[c_index][1:]:
                        if f_name == s[0]:
                            fun_signature = s
                            break
                    print("FUN SIG: ", fun_signature)
                    args = calls[calls.index('"') + 1:]
                    print("Bef Func Args:", args)
                    char = ''
                    ind = 0
                    open_count = 0
                    close_count = 0
                    for char in args:
                        ind += 1
                        if char == '"':
                            break

                    balances = args[:ind + 1]
                    print("Balances:", balances)
                    args = args[ind + 1:]
                    value = 0
                    if ',' in args:
                        end = args.index(',')
                        value = args[:end]
                    else:
                        end = args.index(')') - 1
                        value = args[:end + 1]
                    params = args[end + 1:-1]
                    # TODO: Handle structures!!!!
                    params = params.split(',')
                    sender = params[0]
                    params = params[1:]
                    sender = hex(int(sender))
                    sender = to_checksum_address(sender.ljust(42, '0').upper()[2:])
                    init_ch = 9
                    index_p = 0
                    while len(fun_signature) > init_ch:
                        if(fun_signature[init_ch - 1] == 'address'):
                            params[index_p] = hex(int(params[index_p]))
                            print("OLD LEN: ", len(str(params[index_p])))
                            params[index_p] = to_checksum_address(params[index_p].ljust(42, '0').upper()[2:])
                            # params[index_p]= '0x' + params[index_p]
                            print("NEW PARAMS: ", params[index_p])
                        if(fun_signature[init_ch - 1] == 'string'):
                            params[index_p] = params[index_p].split("=")[1]
                        index_p+=1
                        init_ch+=2
                    args = '(' + ','.join(params) + ')'
                    print("Function args:", args)
                    print("Value:", value)
                    print("Sender:", sender)
                    ucall = f_name + args
                    if(str(sender) == "0x0000000000000000000000000000000000000000"):
                        sender = random.randint(1000000000, 100000000000000000000)
                        sender = hex(int(sender))
                        sender = to_checksum_address(sender.ljust(42, '0').upper()[2:])
                    test_body.append("\t\tvm.prank("+sender+");\n")
                    if(int(value) > 0):
                        test_body.append("\t\tvm.deal("+sender+", " + str(value) +" wei );\n")
                        ucall = f_name + "{ value: " + value + " wei }" + args
                        print("Unique address!")
                    test_body.append("\t\t{}.{}; //{}\n".format(contract_vars[c_index], ucall, calls))
                test_body.append("\t}\n")

        out = header + fields + ["\tfunction setUp() public {\n"] + setUp + ["\t}\n"] \
              + test_body + ["}\n"]

        test_file.writelines(out)
        test_file.close()


if __name__ == '__main__':
    tw = TestWrapper("../sandbox/testgen.txt",
                     [[['C', 'contract'], ['test', 'uint256', 'a', 'uint256', 'b']]])  # nested_if
    tw = TestWrapper("../sandbox/testgen.txt",
                     [[['C', 'contract', 'uint256', 'b'], ['f', 'uint256', 'x'], ['set_max', 'uint256', 'x', 'uint256', 'y']]])  # contract_1.sol
    tw = TestWrapper("../sandbox/testgen.txt",
                     [[['A', 'contract', 'uint256', 'a'], ['f']],
                      [['B', 'contract', 'uint256', 'b'], ['f'], ['g']]])  # contract_3.sol
    # tw = TestWrapper("../sandbox/testgen.txt", [[['C', 'contract'], ['simple_if', 'uint256']]])  # simple_if
    [print(e) for e in tw.wrap()]
    # cleaned = tw.remove_duplicates(tw.wrap())
    tw.generate_sol_test(tw.wrap(), "constructor_3")
    # [print(e) for e in cleaned]
    # python script to generate Solidity Tests from Raw log and signature of Sol file
