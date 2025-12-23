import argparse
import time
from datetime import datetime
import os
import shutil
import subprocess
import solTg.SolidityTestGen as SolidityTestGen
from solTg.ReportBuilder import html_report

""" Tools location
"""


def init():
    global SOURCE_PATH, SANDBOX_DIR, OUTPUTDIR, TIMEOUT
    # tmp = os.path.dirname(os.path.dirname((os.path.dirname(os.path.realpath(__file__)))))
    tmp = os.getcwd()
    SANDBOX_DIR = tmp + "/sandbox"
    OUTPUTDIR = tmp + "/test"
    TIMEOUT = 120

def clean_dir(dir):
    for root, dirs, files in os.walk(dir):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    if not os.path.exists(dir):
        os.mkdir(dir)


def copy_dir(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)


def move_to_sandbox(files):
    print("========move_to_sandbox===========")
    if not os.path.exists(SANDBOX_DIR):
        os.mkdir(SANDBOX_DIR)
    else:
        print('clear output directory {}'.format(SANDBOX_DIR))
        # remove dir
        os_info = os.uname()
        if (os_info.sysname != 'Darwin'):
            clean_dir(SANDBOX_DIR)
        else:
            shutil.rmtree(SANDBOX_DIR)
            os.mkdir(SANDBOX_DIR)
    new_file_list = []
    for f in files:
        # create subdir for each .c file
        basename = os.path.basename(f)
        name_wo_ext = os.path.splitext(basename)[0]
        subdir = SANDBOX_DIR + "/" + name_wo_ext
        os.mkdir(subdir)
        # copy file to individual sandbox
        new_file = subdir + "/" + basename
        shutil.copyfile(f, new_file)
        new_file_list.append(new_file)
    return new_file_list



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


def command_executer(command, timeout, file):
    print("command: {}".format(str(command)))
    logger(file, " ".join(command))
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            mesage = 'command: {} has been killed after timeout {}'.format(" ".join(command), timeout)
            print(mesage)
            stdout, stderr = process.communicate()
            logger(file, str(stdout))
            logger(file, str(stderr))
        except Exception:
            process.kill()
            process.wait()
            mesage = 'command: {} has been killed after timeout {}'.format(" ".join(command), timeout)
            print(mesage)
            logger(file, mesage)
            raise
        retcode = process.poll()
        logger(file, [process.args, retcode, stdout, stderr])
        if retcode and retcode != 254:
            return False
        else:
            return True


def main_pipeline(files):
    global SOURCE_PATH, SANDBOX_DIR, OUTPUTDIR, RERUN
    if RERUN:
        clean_dir(OUTPUTDIR)
    print("number of files: {}".format(len(files)))
    for i, f in enumerate(sorted(files)):
        start_time = time.time()
        print("{:.2f}".format(100 * i / len(files)), "%", f)
        print(i)
        ff = os.path.abspath(f)
        basename = os.path.basename(ff)
        dirname = os.path.dirname(ff)
        print("basename: {}".format(basename))
        print("dirname: {}".format(dirname))
        base_dirname = os.path.basename(dirname)
        dir_dirname = os.path.dirname(dirname)
        print("base_dirname: {}".format(base_dirname))
        print("dir_dirname: {}".format(dir_dirname))
        # Step 1: run SolidityTestGen.py -i f
        SolidityTestGen.main(f, TIMEOUT)
        # Step 2: mkdir: OUTPUTDIR + "/" + base_dirname
        new_sub_dir = OUTPUTDIR + "/" + base_dirname
        if not os.path.exists(new_sub_dir):
            os.mkdir(new_sub_dir)
        # Step 3. copy sanbox to new_dir_path
        new_dir_path = OUTPUTDIR + "/" + base_dirname + "/" + os.path.splitext(basename)[0]
        copy_dir(SANDBOX_DIR, new_dir_path)

        to_print_var = 'total time: {} seconds'.format(time.time() - start_time)
        #logger(os.path.dirname(f) + '/log.txt', to_print_var)


def main():
    start_time = time.time()
    init()
    global SOURCE_PATH, SANDBOX_DIR, OUTPUTDIR, RERUN, TIMEOUT
    parser = argparse.ArgumentParser(description='python script to run Sol Test Generation for all files in dir')
    insourse = ['-i', '--input_source']
    kwsourse = {'type': str, 'help': 'Input .sol-file. or directory with .sol-files'}

    # outdir = ['-o', '--output_dir']
    # kwoutdir = {'type': str, 'help': 'Output direcory name. Default: OUTPUTDIR = ../testgen_output.'}
    
    timeout = ['-t', '--timeout']
    kwtimeout = {'type': int, 'help': 'integer time in seconds. Default: 120'}

    parser.add_argument(*insourse, **kwsourse)
    # parser.add_argument(*outdir, **kwoutdir)
    parser.add_argument(*timeout, **kwtimeout)
    kwcov = {'type': bool, 'help': 'true - rerun / false - continue. Default: true.'}
    parser.add_argument('--rerun', **kwcov)

    args = parser.parse_args()

    RERUN = True
    if args.rerun is not None:
        if args.rerun == 'false':
            RERUN = False
        if args.rerun == 'true' or args.rerun == 'True':
            RERUN = True

    print(RERUN)

    files = []
    if args.input_source is not None:
        if os.path.isfile(args.input_source):
            file = args.input_source
            print('input file was set to {}'.format(file))
            files = [file]
        elif os.path.isdir(args.input_source):
            print('input directory was set to {}'.format(args.input_source))
            SOURCE_PATH = args.input_source
            files = sorted([os.path.join(dp, f) for dp, dn, filenames in os.walk(SOURCE_PATH)
                            for f in filenames if os.path.splitext(f)[1] == '.sol'
                            and os.path.splitext(f)[0] != "harness"])
            if not RERUN: # if rerun flase => find all finished files in testgen_output (-o: dir)
                destination = os.path.abspath(args.output_dir)
                subdirs = [f.path for f in os.scandir(destination) if f.is_dir() and os.path.basename(f)]
                al_run = []
                for sd in subdirs:
                    al_run += [f.path for f in os.scandir(sd) if f.is_dir() and os.path.basename(f)]
                al_run = [os.path.basename(a) + ".sol" for a in al_run]
                new_files = []
                for f in files:
                    if os.path.basename(f) not in al_run:
                        new_files.append(f)
                files = new_files # update all files and include only NOT fished file
        else:
            print('invalid input_source: {}'.format(args.input_source))
            exit(1)
    if args.timeout is not None:
        TIMEOUT = args.timeout
        print(f"timeout set to {TIMEOUT}")
    
    # if args.output_dir is not None:
    #     print('sandoutput dir set to {}'.format(args.output_dir))
    #     OUTPUTDIR = args.output_dir

    for f in files:
        print(f)
    main_pipeline(files)
    html_report.buildReport(OUTPUTDIR)
    # html_report.build_excel_report(OUTPUTDIR)
    # clean_dir(SANDBOX_DIR)
    # os.rmdir(SANDBOX_DIR)
    # html_report.buildReport_Excel_klee(SANDBOX_DIR)
    tt = time.time() - start_time
    to_print_var = 'total time: {} seconds'.format(tt)
    print(to_print_var)


if __name__ == "__main__":
    main()