from pynput.keyboard import *
from pynput import mouse
import threading
import multiprocessing
from multiprocessing import *
import hashlib
import argparse
import configparser
import signal
import subprocess
import logging

global isGen
global mouse_x
global lock_mx
global mouse_y
global lock_my
global blocks
global xtrlock_proc
global xtrlock_path
global lock
xtrlock_path = "/usr/bin/xtrlock"
mouse_x = 1
mouse_y = 1
pwd_len = 6
pwd_chrs = "---"
pwd_hsh = "nah"
do_output = False

lock = threading.Lock()


class Block:
    x1 = 0
    y1 = 0
    x2 = 100
    y2 = 100
    value = "nah"

    def __init__(self, x1=0, y1=0, x2=100, y2=100, value="nah"):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.value = str(value)
        pass

    def check(self, x, y):
        if (x >= self.x1 and x <= self.x2 and y >= self.y1 and y <= self.y2):
            return True
        else:
            return False
        pass

    def info(self):
        return "Area:({}, {}) to ({}, {}) with value {}".format(
            self.x1, self.y1, self.x2, self.y2, self.value)


blocks = [
    #block0, block1, block3, block4, block5, block6, block7, block8, block9,
    #block_total
]
block_total = Block()


def on_press(key):
    print('{0} pressed'.format(key))
    pass


def on_release(key):
    #print('{0} release'.format(key))
    pass


def on_move(x, y):
    global do_output, pwd_hsh, pwd_len, pwd_chrs
    #if do_output: print('Pointer moved to {0}'.format((x, y)))
    #ohash = hashlib.md5((str(x) + str(y)).encode('utf-8')).hexdigest()
    #print(str(ohash))
    global lock_mx, lock_my
    global blocks, block_total, lock
    lock_mx = x
    lock_my = y
    with lock:
        if block_total.check(x, y):
            for b in blocks:
                if b.check(x,
                           y) and b.value != "nah" and b.value != pwd_chrs[-1]:
                    #if do_output:
                    #    print(b.value + ":" + pwd_chrs[-1] + ":" + pwd_chrs)
                    if len(pwd_chrs) < pwd_len:  #len<
                        pwd_chrs += b.value
                        pass
                    else:  #len=>
                        pwd_chrs = pwd_chrs[1:] + b.value
                        pass
                    if do_output: print(b.value + ":" + pwd_chrs)
                    pass
                pass
            pass
        global xtrlock_proc
        if pwd_chrs.__len__() - pwd_chrs.count("-") == pwd_len and hash(
                pwd_chrs) == pwd_hsh:
            #******************************Correct exit*********************************#
            print("Successfully unlocked:{} / {}".format(pwd_chrs, pwd_hsh))
            screen_lock(False)
            os.kill(os.getpid(), signal.SIGTERM)
            pass
        pass
    pass


def on_click(x, y, button, pressed):
    #print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
    if not pressed:
        # Stop listener
        return False


def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))


def kb_init():
    with Listener(on_press=on_press, on_release=on_release) as kb_listener:
        kb_listener.join()


def ms_init():
    with mouse.Listener(
            on_move=on_move, on_click=on_click,
            on_scroll=on_scroll) as ms_listener:
        ms_listener.join()


def create_default(path):
    print("Pharsing default and writing to " + path)
    config = configparser.ConfigParser()
    config.add_section(section="Setting")
    config.set(section="Setting", option="PwdLen", value='6')
    config.set(section="Setting", option="PwdHsh", value='1')
    config.set(section="Setting", option="SizeX1", value='1000')
    config.set(section="Setting", option="SizeY1", value='1000')
    config.set(section="Setting", option="SizeX2", value='1000')
    config.set(section="Setting", option="SizeY2", value='1000')
    config.set(
        section="Setting", option="Xtrlock_path", value="/usr/bin/xtrlock")
    config.write(open(path, 'w+', encoding='utf_8_sig'))
    pass


def main():  #TODO: display, logging
    global isGen
    global mouse_x
    global lock_mx
    global mouse_y
    global lock_my
    global blocks
    global lock
    parser = argparse.ArgumentParser(description='xtrlock')
    parser.add_argument(
        '-g',
        '--gen',
        action='store',
        type=bool,
        dest="gen",
        help="record pwd and generate the config file",
        default=False)
    parser.add_argument(
        '-c',
        '--config_file',
        action='store',
        type=str,
        dest="config_file",
        help="specify the config file to use/write, default as xtrlock.conf",
        default="xtrlock.conf")

    args = parser.parse_args()

    print(args.gen)  #do record?
    global isGen
    isGen = args.gen
    print("generate file: " + str(isGen))

    print(args.config_file)  #where to record
    global config_file
    config_file = args.config_file
    print(config_file)

    if (isGen):  #generate
        #kb_proc = multiprocessing.Process(target=kb_init, args=())
        #kb_proc.start()
        #ms_proc = multiprocessing.Process(target=ms_init, args=())
        #ms_proc.start()
        kb_t = threading.Thread(target=kb_init, args=())
        #kb_t.setDaemon(True)
        #kb_t.start()#keyboard is unnecessary till now#
        ms_t = threading.Thread(target=ms_init, args=())
        #ms_t.setDaemon(True)
        ms_t.start()
        if not os.access(config_file, os.R_OK) or not os.path.exists(
                config_file) or not os.path.isfile(config_file):
            print("config file not found, generating:")
            create_default(config_file)
            pass

        try:
            print("Reading config file from: " + config_file)
            cp = configparser.ConfigParser()
            cp.read(config_file, encoding="utf-8-sig")
            read_conf(cp)
            update_conf(config_file, cp)
            cp.write(open(config_file, 'w+', encoding='utf_8_sig'))

        except Exception as e:
            print(
                "Failed to read config file, config backed up at .bak, now creating default: "
                + str(e))
            open(
                config_file + ".bak",  #backup the old broken config
                "w+").writelines(open(config_file, "r+"))
            create_default(config_file)
            pass
        pass

    else:  #use
        try:
            print("Reading config file from: " + config_file)
            cp = configparser.ConfigParser()
            cp.read(config_file, encoding="utf-8-sig")
            read_conf(cp)
            print("config_file read")
            kb_t = threading.Thread(target=kb_init, args=())
            #kb_t.setDaemon(True)
            kb_t.start()
            ms_t = threading.Thread(target=ms_init, args=())
            #ms_t.setDaemon(True)
            ms_t.start()
            screen_lock(True)
            xtrlock_proc.wait()
        except Exception as e:
            print("Error:" + str(e))
            pass

        pass

    os.kill(os.getpid(), signal.SIGTERM)
    pass


def read_conf(cp):
    #xtrlock_path
    global xtrlock_path
    xtrlock_path = cp.get(section="Setting", option="Xtrlock_path")
    #SizeX1/Y1
    x1 = cp.getint(section="Setting", option="SizeX1")
    x2 = cp.getint(section="Setting", option="SizeX2")
    y1 = cp.getint(section="Setting", option="SizeY1")
    y2 = cp.getint(section="Setting", option="SizeY2")
    update_blocks(x1, y1, x2, y2)

    #pwd
    global pwd_len, pwd_chrs, pwd_hsh, do_output, lock
    pwd_hsh = cp.get(section="Setting", option="PwdHsh")
    pwd_len = cp.getint(section="Setting", option="PwdLen")
    do_output = True
    pass


def update_conf(path, cp):
    print("Please enter the new config (enter to use the old value)")
    #xtrlock_path
    global xtrlock_path
    new_path = input(
        "enter path to your xtrlock installation(`whereis xtrlock`)({}):".
        format(cp.get(section="Setting", option="Xtrlock_path")))
    if new_path != '':
        xtrlock_path = new_path
        cp.set(section="Setting", option="Xtrlock_path", value=str(x1))
        pass

    #SizeX1/Y1
    input("SizeX1/Y1(enter to set current mouse position as the first point)")
    x1 = lock_mx
    y1 = lock_my
    print("Point 1 Set to:" + str(x1) + ', ' + str(y1))

    #SizeX2/Y2
    input("SizeX2/Y2(enter to set current mouse position as the second point)")
    x2 = lock_mx
    y2 = lock_my
    print("Point 2 Set to:" + str(x2) + ', ' + str(y2))
    cp.set(section="Setting", option="SizeX1", value=str(x1))
    cp.set(section="Setting", option="SizeX2", value=str(x2))
    cp.set(section="Setting", option="SizeY1", value=str(y1))
    cp.set(section="Setting", option="SizeY2", value=str(y2))
    update_blocks(x1, y1, x2, y2)

    #pwd
    global pwd_len, pwd_chrs, pwd_hsh, do_output, lock
    new_len = input("enter the length of the pattern(e.g: 5 for 12345)(" +
                    cp.get("Setting", "PwdLen") + "):")
    if new_len != '':
        cp.set(section="Setting", option="PwdLen", value=new_len)
        pwd_len = int(new_len)
        pass
    else:
        pwd_len = cp.getint("Setting", "PwdLen")
        pass

    #new_pwd_chrs=""
    while True:
        wipe_pwd()
        do_output = True
        input(
            "use the mouse to create the pattern in the area set and press enter to confirm):"
        )
        if pwd_chrs.__len__() - pwd_chrs.count("-") == pwd_len:
            new_pwd_chrs = pwd_chrs
            print("pwd set at {}".format(pwd_chrs))
            break
        else:
            print("pwd not long enough: {}/{}".format(
                pwd_chrs.__len__() - pwd_chrs.count("-"), pwd_len))
        pass

    with lock:
        new_hsh = hash(pwd_chrs)  #critical
        wipe_pwd()
        pwd_hsh = new_hsh
        print("New password {} set with hashed value {}".format(
            new_pwd_chrs, pwd_hsh))
        cp.set(section="Setting", option="PwdHsh", value=pwd_hsh)
        #wipe_pwd()
        pass
    pass


def wipe_pwd():
    global pwd_len, pwd_chrs, pwd_hsh, do_output, lock
    pwd_chrs = ""
    for i in range(0, pwd_len):
        pwd_chrs += ("-")
        pass
    pass


def update_blocks(x1, y1, x2, y2, section_w=3, section_h=3, gap_rate=0.13):
    global trigger
    global isGen
    global mouse_x
    global lock_mx
    global mouse_y
    global lock_my
    #regularize x1->x2, y1->y2: 0->100, 0->100 x=l2r,y=u2d
    if (x1 > x2):
        x1, x2 = x2, x1
        print("Auto flipped location x")
        pass
    if (y1 > y2):
        y1, y2 = y2, y1
        print("Auto flipped location y")
        pass

    #find label
    global block_total
    block_total = Block(x1, y1, x2, y2)
    print(block_total.info())

    gapx = abs(x2 - x1) * gap_rate
    gapy = abs(y2 - y1) * gap_rate

    block_w = int((abs(x2 - x1) - (gapx * (section_w - 1))) / (section_w))
    block_h = int((abs(y2 - y1) - (gapy * (section_h - 1))) / (section_h))

    print("W per block: {} with gap {}, H per block: {} with gap {}".format(
        gapx, block_w, block_h, gapy))

    block_value = 1
    buf_x1, buf_y1, buf_x2, buf_y2 = x1, y1, x1 + block_w, y1 + block_h

    for ih in range(0, section_h):
        for iw in range(0, section_w):
            block = Block(buf_x1, buf_y1, buf_x2, buf_y2, block_value)
            blocks.append(block)  #add at first
            print(block.info())
            block_value += 1
            buf_x1 += gapx + block_w  #x1->1
            buf_x2 += gapx + block_w  #x2->1
            pass
        buf_y1 += 0 + gapy + block_h  #br
        buf_y2 += 0 + gapy + block_h  #br
        buf_x1 = x1
        buf_x2 = x1 + block_w
        pass
    pass


def hash(string):
    return hashlib.md5(
        str(string).encode("utf-8")).hexdigest()  #.encode('utf-8').hexdigest()


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid,
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
    pass


def screen_lock(islock):
    global xtrlock_proc
    if islock:
        xtrlock_proc = subprocess.Popen(
            args=(xtrlock_path, "-p123", "-n"), stdout=subprocess.PIPE)
        print("Successfully locked")
        pass
    else:
        xtrlock_proc.kill()
        pass
    pass


if __name__ == '__main__':
    main()
