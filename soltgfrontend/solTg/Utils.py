import os.path
from datetime import datetime
import matplotlib.pyplot as plt

def read_log(filename):
    if not os.path.isfile(filename):
        return None
    lines = open(filename, 'r').readlines()
    results = []
    for line in lines:
        if 'rq_t' in line:
            tmp = line.strip().split()
            if len(tmp) >= 6:
                results.append(tmp[5])
    return results


def plot_ts(times, new_file_abs_path):
    result = [(t - times[i]).total_seconds() for i, t in enumerate(times[1:])]
    x = range(1, len(result) + 1)
    plt.clf()
    plt.plot(x, result)
    plt.xlabel("x - request to z3")
    plt.ylabel('y - time delta')
    plt.title('iteration progress')
    #plt.show()
    plt.savefig(new_file_abs_path)


def generate_plot(log_file, new_file_abs_path):
    times = read_log(log_file)
    print(times)
    try:
        plot_ts([datetime.strptime(t, "%H:%M:%S") for t in times], new_file_abs_path)
    except:
        print("An exception plot_ts")


if __name__ == '__main__':
    generate_plot('log.txt', 'img.png')