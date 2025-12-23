import argparse
import os
import random
import shutil
import subprocess
import time
from datetime import datetime
from sys import platform

from solTg.SolParser import SolParser
from solTg.TestWrapper import TestWrapper
import solTg.Utils as Utils

""" Init SetUp 
"""


def init():
    global ADT_DIR, SOLCMC, CORE, TIMEOUT, SANDBOX_DIR, SOLVER_TYPE, TG_PATH, TG_TIMEOUT, FORGE_PATH, COMP_PATH
    # Dockerfile-solcmc
    SANDBOX_DIR = "../sandbox"
    CORE = os.getcwd() + '/'
    SANDBOX_DIR = CORE + "sandbox"
    if platform == "darwin":
        tmp = os.path.dirname(os.path.dirname((os.path.dirname(os.path.realpath(__file__)))))
        SOLCMC = tmp + "/deps/"
        TG_PATH = tmp + "/deps/tgnonlin"
        # TG_PATH = "/Users/konstantin.britikov/Documents/SMT/mas_fed/aeval/build/tools/nonlin/tgnonlin"
        FORGE_PATH = "forge"
    if platform == "linux" or platform == "linux2":
        # tmp = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname((os.path.dirname(os.path.realpath(__file__)))))))
        tmp = "/home/kabir-nagpal/Desktop/soltgp/soltgfrontend"
        SOLCMC = "/home/kabir-nagpal/Desktop/soltgp/soltgfrontend/deps/"
        TG_PATH = tmp + "/deps/tgnonlin"
        COMP_PATH = tmp + "/deps/solc"
        FORGE_PATH = "forge" # "/home/fmfsu/.foundry/bin/forge"
    TIMEOUT = 600
    SOLVER_TYPE = "z3"  # "eld" # "z3"


def clean_dir(dir):
    for root, dirs, files in os.walk(dir):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def prepare_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    else:
        print('clear output directory {}'.format(dir))
        # remove dir
        os_info = os.uname()
        if (os_info.sysname != 'Darwin'):
            clean_dir(dir)
        else:
            shutil.rmtree(dir)
            os.mkdir(dir)


def move_to_sandbox(files, add_h, was_cleaned):
    print("========move_to_sandbox===========")


""" write content to the file"""


def logger(file, content):
    f = open(file, 'a')
    now = datetime.now()
    time = now.strftime("%H:%M:%S:%f")
    t = str('[{}]'.format(time))
    if type(content) is list:
        f.writelines([t] + ['\n'])
        for c in content:
            if type(c) is list:
                f.writelines([' '.join(c)] + ['\n'])
            elif type(c) is bytes:
                cs = str(c)
                list_to_print = [f + '\n' for f in cs.split('\\n')]
                f.writelines(list_to_print + ['\n'])
            else:
                f.writelines([str(c)] + ['\n'])
    elif type(content) is str:
        f.write(t + '\n' + content + '\n')
    f.close()


""" converts list ot string with spaces"""


def list_to_string(lst):
    return ' '.join([str(e) for e in lst])


def command_executer_tg(command, timeout, log_file, output_file):
    print("command: {}".format(str(command)))
    # f = open(output_file, "a")
    # f.flush()
    # logger(log_file, list_to_string(command))
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
            logger(log_file, str(stdout))
            logger(log_file, str(stderr))
        except Exception:
            process.kill()
            stdout, stderr = process.communicate()
            logger(log_file, process.stdout.read())
            logger(log_file, process.stderr.read())


def command_executer_err(command, timeout, log_file, output_file):
    print("command: {}".format(str(command)))
    f = open(output_file, "a")
    logger(log_file, list_to_string(command))
    with subprocess.Popen(command, stdout=f, stderr=f) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            mesage = 'command: {} has been killed after timeout {}'.format(list_to_string(command), timeout)
            print(mesage)
            stdout, stderr = process.communicate()
            #logger(log_file, str(stdout))
            #logger(log_file, str(stderr))
        except Exception:
            process.kill()
            process.wait()
            mesage = 'command: {} has been killed after timeout {}'.format(list_to_string(command), timeout)
            print(mesage)
            logger(log_file, mesage)
            raise
        retcode = process.poll()
        print(f'RETURN CODE IS {retcode}')
        logger(log_file, [process.args, retcode, stdout, stderr])
        if retcode and retcode != 254:
            return False
        else:
            return True

def command_executer(command, timeout, log_file, output_file):
    print("command: {}".format(str(command)))
    f = open(output_file, "a")
    logger(log_file, list_to_string(command))
    with subprocess.Popen(command, stdout=f, stderr=subprocess.PIPE) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            mesage = 'command: {} has been killed after timeout {}'.format(list_to_string(command), timeout)
            print(mesage)
            stdout, stderr = process.communicate()
            #logger(log_file, str(stdout))
            #logger(log_file, str(stderr))
        except Exception:
            process.kill()
            process.wait()
            mesage = 'command: {} has been killed after timeout {}'.format(list_to_string(command), timeout)
            print(mesage)
            logger(log_file, mesage)
            raise
        retcode = process.poll()
        print(f'RETURN CODE IS {retcode}')
        logger(log_file, [process.args, retcode, stdout, stderr])
        if retcode and retcode != 254:
            return False
        else:
            return True
        
def getDGraphFromOutput(graph_file, contract_name):
    stdout = ''
    with open(graph_file, 'rb') as file:
        str_lines = [str(b)[2:-1] for b in file.readlines()]
        print(str_lines)
        stdout = ''.join(str_lines)
    dgraphs = str(stdout).split('(DEPENDANCY-GRAPH-DELIMITER)')
    
    for graph_block in dgraphs:
        if ('(CONTRACT-NAME-DELIMTER)') in graph_block:
            found = False
            for dgraph in graph_block.split('(CONTRACT-NAME-DELIMTER)'):
                if found:
                    return str(dgraph)
                if dgraph == contract_name:
                    found = True

def getDGraphsFromOutput(stdout):
    dgraphs = str(stdout).split('(DEPENDANCY-GRAPH-DELIMITER)')
    s = ''
    for graph_block in dgraphs:
        if ('(CONTRACT-NAME-DELIMTER)') in graph_block:
            print(graph_block)
            s = s + '(DEPENDANCY-GRAPH-DELIMITER)'
            s = s + graph_block
            s = s + '(DEPENDANCY-GRAPH-DELIMITER)'
            # found = False
            # for dgraph in graph_block.split('(CONTRACT-NAME-DELIMTER)'):
            #     if found:
            #         return dgraph
            #     if dgraph == contract_name:
            #         found = True
    # print(s)
    # exit()
    return str(s)

def command_executer_comp(command, timeout, file, contract_name):
    # os.chdir(SANDBOX_DIR)
    print("command: {}".format(str(command)))
    logger(file, list_to_string(command))
    print("File:", file)
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            mesage = 'command: {} has been killed after timeout {}'.format(list_to_string(command), timeout)
            print(mesage)
            stdout, stderr = process.communicate()
            # logger(file, str(stdout))
            # logger(file, str(stderr))
        except Exception:
            process.kill()
            process.wait()
            mesage = 'command: {} has been killed after timeout {}'.format(list_to_string(command), timeout)
            print(mesage)
            logger(file, mesage)
            raise
        retcode = process.poll()
        # logger(file, str(subprocess.CompletedProcess(process.args, retcode, stdout, stderr)))
        logger(file, [process.args, retcode, stdout, stderr])
        if retcode and retcode != 254 and retcode != 137:
            return False
        else:
            # start with "Running with solver" and terminate with "Entire output"
            start = False
            out = []
            
            dGraph = getDGraphsFromOutput(stdout)
            with open(SANDBOX_DIR + '/graph_all.txt' , "w") as graphfile:
                graphfile.write(str(dGraph.replace("\\n", "\n")[0:]))
            
            
            to_check = str(stderr).split("\\n")
            number_of_set_logic_HORN = 0


            for s in to_check:
                if "(set-logic HORN)" in str(s):
                    number_of_set_logic_HORN += 1
                if start:
                    out.append(s + "\n")
                if "(check-sat)" in str(s) or number_of_set_logic_HORN > 1:
                    break
                if "Info: CHC: Requested query:" in str(s):
                    start = True
            # add "(set-option :produce-proofs true)"
            # add "(get-proof)"
            # out.insert(1, "(set-option :produce-proofs true)\n")
            # out.append("(get-proof)\n")
            return out
        
        
def command_executer_docker_solcmc(command, timeout, file):
    # os.chdir(SANDBOX_DIR)
    print("command: {}".format(str(command)))
    logger(file, list_to_string(command))
    print("File:", file)
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            mesage = 'command: {} has been killed after timeout {}'.format(list_to_string(command), timeout)
            print(mesage)
            stdout, stderr = process.communicate()
            # logger(file, str(stdout))
            # logger(file, str(stderr))
        except Exception:
            process.kill()
            process.wait()
            mesage = 'command: {} has been killed after timeout {}'.format(list_to_string(command), timeout)
            print(mesage)
            logger(file, mesage)
            raise
        retcode = process.poll()
        # logger(file, str(subprocess.CompletedProcess(process.args, retcode, stdout, stderr)))
        logger(file, [process.args, retcode, stdout, stderr])
        if retcode and retcode != 254 and retcode != 137:
            return False
        else:
            # start with "Running with solver" and terminate with "Entire output"
            start = False
            out = []
            to_check = str(stdout).split("\\n")
            number_of_set_logic_HORN = 0


            for s in to_check:
                if "(set-logic HORN)" in str(s):
                    number_of_set_logic_HORN += 1
                if "Entire output" in str(s) or number_of_set_logic_HORN > 1:
                    break
                if start:
                    out.append(s + "\n")
                if "Running with solver" in str(s):
                    start = True
            # add "(set-option :produce-proofs true)"
            # add "(get-proof)"
            # out.insert(1, "(set-option :produce-proofs true)\n")
            # out.append("(get-proof)\n")
            return out


def test_1(updated_file_name):
    global SANDBOX_DIR
    command = [COMP_PATH, 
               '--model-checker-solvers=smtlib2', 
               '--model-checker-engine=chc', 
               "--model-checker-print-query",
            #    "--model-checker-ext-calls=trusted",
               updated_file_name]
    command_executer_err(command, 120, SANDBOX_DIR + '/log_test.txt', SANDBOX_DIR + '/help.txt')
    

def run_solcmc(updated_file_name, contract_name):
    # ./docker_solcmc examples smoke_safe.sol Smoke 30 z3
    os.chdir(CORE)
    # shutil.copy(SOLCMC + "run_solcmc", "./run_solcmc")
    # shutil.copy(SOLCMC + "docker_solcmc_updated", "./docker_solcmc_updated")
    basename = os.path.basename(updated_file_name)
    smt_name = os.path.splitext(basename)[0] + '.smt2'
    print("Running solcmc")
    # command = ["./docker_solcmc_updated", "tmp", basename,
    #             contract_name, str(10), SOLVER_TYPE]#, '>', smt_name]
    # source = ('tmp/'  + updated_file_name.split('tmp/')[1])
    command_2 = [COMP_PATH, '--model-checker-solvers=smtlib2', 
                '--model-checker-engine=chc', 
                "--model-checker-print-query",
                # '--model-checker-ext-calls=trusted',
                updated_file_name]
    
    smt2_list = command_executer_comp(command_2, TIMEOUT, CORE+"log.txt", contract_name)
    # smt2_list = command_executer_docker_solcmc(command, TIMEOUT, CORE+"log.txt")
    print("Contract name:", basename)
    print("Output:", smt2_list)
    if not smt2_list:
        return "F"
    # os.remove(CORE + "run_solcmc")
    # os.remove(CORE + "docker_solcmc_updated")
    return smt2_list


# def run_adt_transform(smt2_file, smt2_wo_adt):
#     print("run adt_transform script")
#     save = os.getcwd()
#     os.chdir(SANDBOX_DIR)
#     command = [ADT_DIR, smt2_file]  # , ">", smt2_wo_adt]
#     command_executer(command, 60, SANDBOX_DIR + "/log.txt", smt2_wo_adt)
#     # check case: (const 0)  and performe:
#     # sed -i 's/(const 0)/((as const (Array Int Int)) 0)/' file
#     with open(smt2_wo_adt, "r") as sources:
#         lines = sources.readlines()
#     with open(smt2_wo_adt, "w") as sources:
#         for line in lines:
#             sources.write(re.sub(r'(const 0)', '(as const (Array Int Int)) 0', line))
#     os.chdir(save)


def get_fun_signature(line):
    start = line.index("function") + len("function")
    if line.find(")") < 0:
        # not supported case regression/types/array_aliasing_memory_1.sol,
        # when function declared in multiple lines
        return []
    end = line.index(")", start + 1)
    function_all = line[start:end + 1].strip()
    function_name = function_all[:function_all.index("(")]
    out = [function_name]
    inside = function_all[function_all.index("(") + 1: function_all.index(")")]
    if inside:
        raw_paramentes = inside.split(',')
        for p in raw_paramentes:
            out.append(p.split()[0])
    # ToDo: add types of parameters
    return out


def is_in_contract_type(line):
    tockens = line.split()
    for e in ['interface', 'contract', 'library']:
        if e in tockens:
            return True
    return False


def get_contrac_type(line):
    if 'interface' in line:
        return 'interface'
    if 'contract' in line:
        return 'contract'
    if 'library' in line:
        return 'library'
    return "NaN"


    


def update_file(file, name):
    print("update file: {}".format(file))
    contract_name = name
    f = open(file, "r", encoding='ISO-8859-1')
    lines_to_check = f.readlines()
    addAssert = True
    functionRead = False
    out = []
    for tmp_l in lines_to_check: # ToDo: check if needed later when Excel feature will be ready
        if tmp_l.strip().startswith("//") :
            continue
        index_of_comments = tmp_l.find("//")
        if index_of_comments > 1:
            l = tmp_l[:index_of_comments] + "\n"
        else:
            l = tmp_l
        if "pragma solidity" in l:
            print("pragma solidity is found")
        else:
            # if addAssert and functionRead and ("{" in out[-1]) and not ("}" in out[-1]):
            #     out.append("\t\tassert(true);\n")
            #     addAssert = False
            #     functionRead = False
            out.append(l)
            if "function" in l:
                functionRead = True


    basename = os.path.basename(file)
    updated_file_name = os.path.dirname(file) + "/" + os.path.splitext(basename)[0] + \
                        "_updated" + os.path.splitext(basename)[1]
    f_updated = open(updated_file_name, 'a')
    print("New out:", out)
    f_updated.writelines(out)
    f_updated.close()
    f.close()
    print(updated_file_name)
    print(contract_name)
    test_1(updated_file_name)
    smt2_list = run_solcmc(updated_file_name, contract_name)
    # move to sanbox
    if smt2_list == "F":
        print("ERROR WAS ENCOUNTERED! IMPOSSBLE TO PRODUCE THE CHC ENCODING(POSSIBLY DUE TO THE LACK OF ASSERTS)!")
        return False
    source = CORE + "/tmp"
    for i in range(len(smt2_list)):
        smt2_list[i] = smt2_list[i].replace("\\r", "")
    # smt2_list = smt2_list.replace("", "\\r")
    # print("Source:", source)
    # print("SMT2 list:", smt2_list)
    destination = os.path.abspath(SANDBOX_DIR)
    allfiles = os.listdir(source)
    for e in allfiles:
        if e == "log.txt":
            shutil.move(source + "/" + e, destination + "/log_encoding.txt")
        else:
            shutil.move(source + "/" + e, destination + "/" + e)

    if smt2_list:
        print("Created smt2, will run adt transform")
        smt2_file = SANDBOX_DIR + "/" + os.path.splitext(basename)[0] + "_updated" + ".smt2"
        f_smt = open(smt2_file, 'a')
        f_smt.writelines(smt2_list)
        f_smt.close()
        clean_dir(CORE + "/tmp")
        os.rmdir(CORE + "/tmp")
        os.remove(CORE + "/log.txt")
        # smt2_wo_adt = SANDBOX_DIR + "/" + os.path.splitext(basename)[0] + "_wo_adt.smt2"
        # smt2_wo_adt = SANDBOX_DIR + "/" + os.path.splitext(basename)[0] + "_updated.smt2"
        # run_adt_transform(smt2_file, smt2_wo_adt)
    return True


def move_for_encoding(file, contract_name):
    print("move_for_encoding")
    # check tmp folder in SOLCMC/tmp
    tmp_dir = CORE + "/tmp"
    prepare_dir(tmp_dir)
    new_file = tmp_dir + "/" + os.path.basename(file)
    shutil.copyfile('tmp.sol', new_file)
    os.remove('tmp.sol')
    if update_file(new_file, contract_name):
        return True
    return False


def convert_for_tg(signature):
    # format contract_name,p1,p2,p2;function_name_1,p1,p2..pn
    out = []
    print("Signature:", signature)
    for c in signature:
        index = 0
        if 'contract' in c[0]:
            print("Contract: ", c)
            contract_name = c[0][0]
            contract_id = c[0][2]
            var_names = [e for i, e in enumerate(c[0][3:]) if i % 2 == 1]
            print("Vars: ", var_names)
            var_str = ','.join(var_names)
            out.append("contract_{}_{}:{}".format(contract_name, contract_id, var_str))
            index = 1
        for f in c[index:]:
            function_name = f[0]
            function_id = f[1]
            var_names = [e for i, e in enumerate(f[2:]) if i % 2 == 1]
            var_str = ','.join(var_names)
            out.append("{}_{}:{}".format(function_name, function_id, var_str))

    return '^'.join(out)


def run_tg(file, signature):
    global SANDBOX_DIR
    basename = os.path.basename(file)
    smt_name = os.path.splitext(basename)[0] + "_updated.smt2"
    # smt_name = os.path.splitext(basename)[0] + "_wo_adt.smt2"
    graph_file_all = SANDBOX_DIR + '/' + 'graph_all.txt'
    contract_name = find_contract_name(signature)
    dgraph = getDGraphFromOutput(graph_file_all, contract_name)
    graph_contract = SANDBOX_DIR + '/' + f'graph_{contract_name}.txt'
    with open(graph_contract , "w") as graphfile:
        graphfile.write(str(str(dgraph).replace("\\n", "\n")[1:]))
    new_smt_file_name = SANDBOX_DIR + "/" + smt_name
    graph_file_name = graph_contract
    print("run TG with".format(new_smt_file_name))
    logger(SANDBOX_DIR + '/log.txt', "run TG with".format(new_smt_file_name))
    signature_for_tg = convert_for_tg(signature)
    print("TG: ", signature_for_tg)
    command_tg = [TG_PATH, "--keys", signature_for_tg, graph_file_name,new_smt_file_name]
    log_file = SANDBOX_DIR + "/log.txt"
    logger(log_file, ' '.join(command_tg))
    print(signature)
    SANDBOX_DIR = os.path.abspath(SANDBOX_DIR)
    save = os.getcwd()
    os.chdir(SANDBOX_DIR)
    command_executer(command_tg, TG_TIMEOUT, log_file, log_file)
    os.chdir(save)


def is_fun_supported(fun_signature):
    # currently only int formate is supported
    for f in fun_signature:
        #if f != "uint":
        if "uint" not in f:
            return False
    return True


def generate_stub(file_name, signature):
    name_wo_extension = os.path.splitext(file_name)[0]
    test_name = name_wo_extension + ".t.sol"
    test_file_full_path = CORE + "/test/" + test_name
    test_file = open(test_file_full_path, 'w')
    out = ["//Generated Test by TG\n", "//{}\n".format(str(signature)),
           "pragma solidity ^0.8.13;\n\n",
           "import \"forge-std/Test.sol\";\n",
           "import \"./{}.sol\";\n\n".format(name_wo_extension),
           f'contract {name_wo_extension}_Test is Test' + ' {\n']

    # contracts declaration
    for i, c in enumerate(signature):
        if c[0][1] in ['contract', 'library']:  # skip interphases
            out.append("\t{} {};\n".format(c[0][0], "c" + str(i)))

    # generate setUp function
    out.append("\n")
    out.append("\tfunction setUp() public {\n")
    for i, c in enumerate(signature):
        if c[0][1] in ['contract', 'library']: # skip interphases
            out.append("\t\t{} = new {}();\n".format("c" + str(i), c[0][0]))
    out.append("\t}\n")

    # generate Tests : one test for each function for each contract
    index = 0
    out.append("\n")
    for i, c in enumerate(signature):
        if len(c) > 1 and c[0][1] in ['contract', 'library']: # skip interphases
            for j, funcs in enumerate(c[1:]):
                check = is_fun_supported(funcs[1:])
                if check:
                    #generate random content
                    content = ','.join([str(random.randint(1, 30)) for e in funcs[1:]])
                    out.append(f'\tfunction test_{name_wo_extension}_{index}() public ' + '{\n')
                    out.append("\t\t{}.{}({});\n".format("c" + str(i), funcs[0], content))
                    out.append("\t\tassertTrue(true);\n\t}\n")
                    index += 1

    out.append("}\n")
    test_file.writelines(out)
    test_file.close()

# def run_test(file, signature):
#     global  SANDBOX_DIR
#     basename = os.path.basename(file)
#     new_name = SANDBOX_DIR + "/" + basename
#     print("Run tests for: {} ".format(new_name))
#     save = os.getcwd()
#     # get test from log
#     # generate_stub(basename, signature)
#     # copy source file to "scr"
#     local_path = os.getcwd()
#     print(local_path + "/src/" + basename)
#     print(f"Source file path", file)
#     # shutil.copyfile(file, local_path + "/src/" + basename)
#     #run command:  forge test --match name
#     SANDBOX_DIR = os.path.abspath(SANDBOX_DIR)
#     logger(SANDBOX_DIR + "/log.txt", "new signature" + str(signature))
#     #os.chdir("../")
#     os.chdir(local_path)
#     command_executer([FORGE_PATH, 'clean'], 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/log.txt")
#     command = [FORGE_PATH, 'test',  str(os.path.splitext(basename)[0])]
#     command_executer(command, 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/test_results.txt")
#     command = [FORGE_PATH, 'coverage',  str(os.path.splitext(basename)[0]), '--report', 'lcov']
#     command_executer(command, 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/test_results.txt")
#     command = [FORGE_PATH, 'coverage', str(os.path.splitext(basename)[0]), '--report', 'summary']
#     command_executer(command, 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/test_results.txt")
#     #copy lcov file
#     if os.path.isfile("lcov.info"):
#         shutil.move("lcov.info", SANDBOX_DIR + "/lcov.info")
#         genhtml_report_command = ['genhtml', '--branch-coverage', '--output', SANDBOX_DIR + '/generated-coverage', SANDBOX_DIR + "/lcov.info"]
#         command_executer(genhtml_report_command, 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/log.txt")
#     os.chdir(save)
#     #os.remove("../src/" + basename)
#     # clean_dir(local_path + "/src")
#     shutil.move(local_path + "/test/" + os.path.splitext(basename)[0] + ".t.sol",
#                 SANDBOX_DIR + "/" + os.path.splitext(basename)[0] + ".t.sol")
#     # clean_dir(local_path + "/test")

def run_test(file, signature):
    global  SANDBOX_DIR
    basename = os.path.basename(file)
    new_name = SANDBOX_DIR + "/" + basename
    print("Run tests for: {} ".format(new_name))
    save = os.getcwd()
    # get test from log
    # generate_stub(basename, signature)
    # copy source file to "scr"
    local_path = os.getcwd()
    print(local_path + "/src/" + basename)
    os.makedirs(local_path + "/src/", exist_ok=True)
    file_src_all = SANDBOX_DIR + "/" + basename
    shutil.copyfile(file_src_all, local_path + "/src/" + basename)
    print(f"Path to file:{file_src_all}")
    #run command:  forge test --match name
    SANDBOX_DIR = os.path.abspath(SANDBOX_DIR)
    logger(SANDBOX_DIR + "/log.txt", "new signature" + str(signature))
    #os.chdir("../")
    os.chdir(local_path)
    command_executer([FORGE_PATH, 'clean'], 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/log.txt")
    command = [FORGE_PATH, 'test',  str(os.path.splitext(basename)[0])]
    command_executer(command, 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/test_results.txt")
    command = [FORGE_PATH, 'coverage',  str(os.path.splitext(basename)[0]), '--report', 'lcov']
    command_executer(command, 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/test_results.txt")
    command = [FORGE_PATH, 'coverage', str(os.path.splitext(basename)[0]), '--report', 'summary']
    command_executer(command, 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/test_results.txt")
    #copy lcov file
    print(os.getcwd())
    if os.path.isfile("lcov.info"):
        print("hello")
        shutil.move("lcov.info", SANDBOX_DIR + "/lcov.info")
        genhtml_report_command = ['genhtml', '--branch-coverage', '--output', SANDBOX_DIR + '/generated-coverage', SANDBOX_DIR + "/lcov.info"]
        command_executer(genhtml_report_command, 60, SANDBOX_DIR + "/log.txt", SANDBOX_DIR + "/log.txt")
    os.chdir(save)
    os.remove(local_path + "/src/" + basename)
    clean_dir(local_path + "/src")
    shutil.move(local_path + "/test/" + os.path.splitext(basename)[0] + ".t.sol",
                SANDBOX_DIR + "/" + os.path.splitext(basename)[0] + ".t.sol")
    # clean_dir(local_path + "/test")


def find_contract_name(signature):
    for s in signature:
        print("SSig:", s)
        if s[0][1] == 'contract':
            return s[0][0]
    return 0



def main(filename, timeout):
    start_time = time.time()
    init()
    global ADT_DIR, SOLCMC, CORE, ADT_DIR, TIMEOUT, SOLVER_TYPE, SANDBOX_DIR, TG_PATH, TG_TIMEOUT, FORGE_PATH
    TG_TIMEOUT = float(timeout)
    print(f"TIMEOUT {timeout}")
    if not filename:
        parser = argparse.ArgumentParser(description='python script for Solidity Test Generation')
        insourse = ['-i', '--input_source']
        kwsourse = {'type': str, 'help': 'Input .c-file. or directory'}
        parser.add_argument(*insourse, **kwsourse)

        args = parser.parse_args()
        print(args)
        file = ""
        if args.input_source is not None:
            if os.path.isfile(args.input_source):
                file = args.input_source
                file = os.path.abspath(file)
                print('solidity input file was set to {}'.format(file))
            elif os.path.isdir(args.input_source):
                print('TBD'.format(args.input_source))
                exit(1)
        else:
            print('invalid input_source: {}'.format(args.input_source))
            exit(1)
    else:
        file = filename


    prepare_dir(SANDBOX_DIR)
    print("File: ", file)
    
    # test_1()

    print("Pre sig")
    signature = SolParser.get_signature(file)
    logger(SANDBOX_DIR + '/log.txt', str(signature))
    contract_name = find_contract_name(signature)
    if contract_name:
        print("In if")
        print("Initial sig: ", signature)
        # ToDo: run tg for each contract
        if not move_for_encoding(file, contract_name):
            return
        for s in signature:
            run_tg(file, [s])
        tw = TestWrapper(SANDBOX_DIR + "/testgen.txt", signature)
        print("LOOK HERE")
        print(signature)
        clean_tests = tw.wrap()
        print(clean_tests)
        clean_tests_wo_duplicats = clean_tests
        if clean_tests:
            if True in [len(t) > 1 for t in clean_tests]:
                logger(SANDBOX_DIR + '/log.txt', "Multiple Calls Test")
        if clean_tests:
            logger(SANDBOX_DIR + '/log.txt', clean_tests)
            if type(clean_tests) is list:
                logger(SANDBOX_DIR + '/log.txt', "# TESTS: {}".format(len(clean_tests)))
            clean_tests_wo_duplicats = tw.remove_duplicates(clean_tests)
            file_name = os.path.basename(file)
            name_wo_extension = os.path.splitext(file_name)[0]
        else:
            logger(SANDBOX_DIR + '/log.txt', "# TESTS: NO TESTS")
        if(clean_tests_wo_duplicats):
            print("THERE ARE TESTS")
            # prepare_dir(CORE + "/test")
            tw.generate_sol_test(clean_tests_wo_duplicats, name_wo_extension, file)
            run_test(file, signature)
            # generate image
            Utils.generate_plot(SANDBOX_DIR + '/log.txt', SANDBOX_DIR + '/imag.png')


    tt = time.time() - start_time
    to_print_var = 'total time: {} seconds'.format(tt)
    print(to_print_var)
    logger(SANDBOX_DIR + '/log.txt', to_print_var)


if __name__ == "__main__":
    main("")
