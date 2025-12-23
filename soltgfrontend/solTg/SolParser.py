import argparse
import json
import os
import shutil
import subprocess


# import docker


def is_supported_type(identifier):
    not_supported = ['array', 'contract', 'enum', 'function_external', 'struct', 'userDefinedValue']
    return not True in [n in identifier for n in not_supported]


class SolParser:
    @classmethod
    def read(self, file):
        if os.path.splitext(file)[1] == ".json":
            f = open(file, "r")
            data = json.load(f)
            # print(data)
            return data
        if os.path.splitext(file)[1] == ".sol":
            command = ['forge', 'flatten', '--output', 'tmp.sol', file]
            subprocess.run(command)
            file_exists = os.path.exists('tmp.sol')

            if not file_exists:
                shutil.copyfile(file, './tmp.sol')

            with open('tmp.sol', 'r') as f:
                lines = f.readlines()

            filtered_lines = [line for line in lines if
                              not line.replace(" ", "").startswith('*') and not line.replace(" ", "").startswith('/**') and not line.replace(" ", "").startswith('/*')]
            with open('tmp.sol', 'w') as f:
                f.writelines(filtered_lines)
            print("FILTERED: ", len(filtered_lines))
            print("NON FILTERED: ", len(lines))
            command = ['solc', 'tmp.sol', '--ast-compact-json']
            # command = ['docker', 'run', '-v', '/Users/konstantin.britikov/Documents/SMT/rand_proj/script:/script/', 'ethereum/solc:0.6.12', "/script/" + file.split("/")[-1], '--ast-compact-json']
            print(command)
            # exit(1)
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                try:
                    stdout, stderr = process.communicate(input, timeout=20)
                    print("Error: ", stderr)
                    stdout_results = stdout.decode("utf-8")
                    stdout_results = stdout_results.replace("\'", "\"")
                    # print("Stdout results: ", stdout_results)
                    next_line = False
                    index = 0
                    print(file)
                    filename = file.split("/")[-1]
                    # print("File: ", file)
                    for i, line in enumerate(stdout_results.split('\n')):
                        print("Iterators: ", i, " : ", line)
                        if next_line:
                            break
                        if filename in line:
                            next_line = True
                            index = i
                    split_arr = stdout_results.split('\n')

                    # print("Splitted: ", split_arr)
                    # print("Splitted len: ", len(split_arr))
                    cut_result = '\n'.join(stdout_results.split('\n')[index + 1:])
                    cut_result = split_arr[-1]
                    # print("Cut result: ", cut_result)
                    # print("Index: ", index)
                    # exit(1)
                    print("CUT: ",stdout_results)
                    data = json.loads(cut_result)
                    # print(data)
                    return data
                except subprocess.TimeoutExpired:
                    process.kill()
                    mesage = 'command: {} has been killed after timeout {}'.format("solc", 20)
                    print(mesage)
                    return []

    @classmethod
    def parse_data(self, data):
        n_of_contracts = len(data['nodes'])
        print("number of contracts: {}".format(n_of_contracts))
        out = []
        
        contracts_from_id = {}
        for n in data['nodes']:
            if n['nodeType'] != "ContractDefinition":
                continue
            id = n['id']
            contracts_from_id[id] = n

        for n in data['nodes']:
            if n['nodeType'] != "ContractDefinition":
                continue
            for_one_contract = []
            name = n['name']
            contract_id = n['id']
            print("name: {} id: {}".format(name, contract_id))
            contractKind = n['contractKind']
            print("Abstract:", n['abstract'])
            if contractKind != "contract" or n['abstract'] == 'True':
                print("Parsing stopped")
                continue
            print("contractKind: {}".format(contractKind))
            p_type1 = 'state_type'
            p_name1 = 'state'
            p_type2 = 'uint'
            p_name2 = 'msg.value'
            p_type3 = 'address'
            p_name3 = 'msg.sender'
            for_one_contract.append([name, contractKind, contract_id, p_type1, p_name1, p_type2, p_name2, p_type3, p_name3])
            print(for_one_contract)
            all_nodes = n['nodes']
            # print("Node: ", f_c)
            signature_nodes = []
            for node in all_nodes:
                if 'kind' not in node:
                    continue
                if ('functionSelector' not in node) and (node['kind'] not in ['constructor', 'fallback', 'receive']):
                    continue
                signature_nodes.append(node)  
            for basecontract_id in n["linearizedBaseContracts"]:
                for node in contracts_from_id[basecontract_id]['nodes']:
                    if 'kind' not in node:
                        continue
                    if ('functionSelector' not in node) and (node['kind'] not in ['fallback', 'receive']) :
                        continue
                    signature_nodes.append(node)
                    
            
            selectors_found = []
            for functionNode in signature_nodes:
                selector = ''
                try:
                    selector = functionNode["functionSelector"]
                except:
                    if functionNode['kind'] in ['constructor', 'fallback', 'receive']:
                        selector = functionNode['kind']
                    else:
                        print("ERROR: Unexpected Node in Signature Nodes")
                        exit()
                
                if selector in selectors_found:
                    continue
                selectors_found.append(selector)
                
                f_name = functionNode['name']
                f_kind = functionNode['kind']
                f_id = functionNode['id']
                f_mutability = functionNode['stateMutability']
                print("Kind:", f_kind)
                print("Name:", f_name)
                print("Id:", f_id)
                print("Mutability:", f_mutability)
                if f_name == "deposit":
                    print(functionNode)
                if f_kind == 'constructor':
                    print(f_name)
                    print("Constructor: ", functionNode)
                    parameters = functionNode['parameters']['parameters']
                    constructor_parameters = []
                    for p in parameters:
                        identifier = p["typeDescriptions"]["typeIdentifier"]
                        if is_supported_type(identifier):
                            constructor_parameters.append(p['typeName']['name'])
                            constructor_parameters.append(p['name'])
                    print("Constructor parameters: ", constructor_parameters)
                    # find [name, contractKind] and add constructor_parameters
                    print("For one con before: ", for_one_contract)
                    for el in for_one_contract:
                        if el[0] == name and el[1] == 'contract':
                            el += constructor_parameters
                    print("For one con after: ", for_one_contract)
                    continue
                elif (f_kind == 'function' or f_kind == 'fallback' or f_kind == 'receive') and (
                        functionNode['visibility'] == 'public' or functionNode['visibility'] == 'external'):
                    tmp_f = [f_kind, f_id]
                    if (f_kind == 'function'):
                        tmp_f = [f_name + '_', f_id]
                    print("FUNCTION:")
                    print("kind: {} name: {} id: {}".format(f_kind, f_name, f_id))
                    params = functionNode['parameters']['parameters']
                    print("# of parameters: {}".format(len(params)))
                    # if f_mutability == 'payable':
                    #     identifier = 'msg'
                    #     p_type = 'tx_type'
                    #     p_name = 'tx'
                    #     tmp_f.append(p_type)
                    #     tmp_f.append(p_name)
                    p_type = 'state_type'
                    p_name = 'state'
                    tmp_f.append(p_type)
                    tmp_f.append(p_name)
                    p_type = 'uint'
                    p_name = 'msg.value'
                    tmp_f.append(p_type)
                    tmp_f.append(p_name)
                    p_type = 'address'
                    p_name = 'msg.sender'
                    tmp_f.append(p_type)
                    tmp_f.append(p_name)
                    # p_type = 'uint'
                    # p_name = 'balanceOf'
                    # tmp_f.append(p_type)
                    # tmp_f.append(p_name)
                    for p in params:
                        identifier = p["typeDescriptions"]["typeIdentifier"]
                        if is_supported_type(identifier):
                            p_type = p['typeName']['name']
                            p_name = p['name']
                            tmp_f.append(p_type)
                            tmp_f.append(p_name)
                        elif 'contract' in identifier:
                            tmp = p['typeDescriptions']['typeString']
                            if 'contract' in tmp:
                                p_type = tmp.split()[1]
                                p_name = p['name']
                            else:
                                continue  # unkown ow type
                        elif not is_supported_type(identifier):
                            tmp_f = []  # enum case or function_external or struct : skip
                        else:
                            if 'name' in p['typeName']['baseType']:
                                p_type = p['typeName']['baseType']['name']
                                p_name = p['name']
                                tmp_f.append(p_type + "[]")
                                tmp_f.append(p_name)
                            else:
                                tmp_f = []  # case of array[][] not supported currently
                                continue
                        # print("type: {}".format(p_type))
                        # print("name: {}".format(p_name))
                    if tmp_f:
                        for_one_contract.append(tmp_f)
                elif f_kind == 'function' and (functionNode['visibility'] == 'private' or functionNode['visibility'] == 'internal'):
                    continue
                else:
                    print("SOMETHING WEIRD")
                    print(f_kind)
                    print(functionNode['visibility'])
                    exit(1)
            if len(for_one_contract) > 1:
                out.append(for_one_contract)
        # exit(1)
        return out

    @classmethod
    def get_signature(self, file):
        d = SolParser.read(file)
        if d:
            return SolParser.parse_data(d)
        else:
            return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='python script for sol file parse')
    insourse = ['-i', '--input_file']
    kwsourse = {'type': str, 'help': 'path: location of the file'}
    parser.add_argument(*insourse, **kwsourse)
    args = parser.parse_args()

    if args.input_file is not None and os.path.isfile(args.input_file):
        f = args.input_file
        print('input file {}'.format(f))
    else:
        exit(1)

    d = SolParser.read(f)
    if d:
        print(SolParser.parse_data(d))
