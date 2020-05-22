import os
import time
from threading import Thread
import traceback


def __write_log__(log, tag=''):
    try:
        log_path = './aq_log/log/'
        log = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())) + '\n' + log + '\n'
        lof_file_name = tag + "_" + str(time.strftime('%Y-%m-%d', time.localtime())) + '.log'
        if os.path.exists(log_path):
            with open(log_path + lof_file_name, 'a', encoding="UTF-8") as file:
                file.write(str(log))
        else:
            os.mkdir(log_path)
            write_log(log)
        return True
    except:
        traceback.print_exc()
        return False


def write_log(log, tag=''):
    t = Thread(target=__write_log__, args=(log, tag))
    t.start()


if __name__ == '__main__':
    write_log('asdsd')
