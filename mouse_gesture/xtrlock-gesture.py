#!/usr/bin/python3
from pynput.keyboard import *
from pynput import mouse
import threading
import multiprocessing
from multiprocessing import *
from ctypes import *
import ctypes
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
global back_up_pwd_hash
global mask

mask = None
back_up_pwd_hash = "ZPxA3rByYGIZc"  #using 123 as default...
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
    clicked = False
    is_master = False

    def __init__(self, x1=0, y1=0, x2=100, y2=100, value="nah"):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.value = str(value)
        pass

    def check(self, x, y):
        if (x >= self.x1 and x <= self.x2 and y >= self.y1 and y <= self.y2):
            if not self.clicked:
                if not self.is_master:
                    self.click()
                self.clicked = True
            return True
        else:
            if self.clicked:
                if not self.is_master:
                    self.draw()
                self.clicked = False
            return False
        pass

    def erase(self):
        mask.erase_square_screen_coord(
            int(self.x1), int(self.y1), int(self.x2), int(self.y2))
        mask.erase_square_screen_coord(
            int(self.x1 + 10), int(self.y1 + 10), int(self.x2 - 10),
            int(self.y2 - 10))
        pass

    def click(self):
        mask.draw_square_screen_coord(
            int(self.x1 + 10), int(self.y1 + 10), int(self.x2 - 10),
            int(self.y2 - 10))
        pass

    def draw(self):
        self.erase()
        mask.draw_square_screen_coord(
            int(self.x1), int(self.y1), int(self.x2), int(self.y2))
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
    #logging.debug('{0} pressed'.format(key))
    pass


def on_release(key):
    #logging.debug('{0} release'.format(key))
    pass


def on_move(x, y):
    global do_output, pwd_hsh, pwd_len, pwd_chrs
    #if do_output: logging.info('Pointer moved to {0}'.format((x, y)))
    global lock_mx, lock_my
    global blocks, block_total, lock
    lock_mx = x
    lock_my = y
    #with lock:
    if (lock.acquire()):
        if block_total.check(x, y):
            for b in blocks:
                if b.check(x,
                           y) and b.value != "nah" and b.value != pwd_chrs[-1]:
                    if len(pwd_chrs) < pwd_len:  #len<
                        pwd_chrs += b.value
                        pass
                    else:  #len=>
                        pwd_chrs = pwd_chrs[1:] + b.value
                        pass
                    if do_output: print(b.value + ":" + pwd_chrs + "\r")
                    pass
                pass
            pass

        global xtrlock_proc
        if pwd_chrs.__len__() - pwd_chrs.count("-") == pwd_len and hash(
                pwd_chrs) == pwd_hsh:
            #******************************Correct exit*********************************#
            logging.info("Successfully unlocked:{} / {}".format(
                pwd_chrs, pwd_hsh))
            screen_lock(False)
            os.kill(os.getpid(), signal.SIGTERM)
            pass
        pass
    lock.release()
    pass


def on_click(x, y, button, pressed):
    #logging.info('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
    if not pressed:
        # Stop listener
        return False


def on_scroll(x, y, dx, dy):
    logging.debug('Scrolled {0} at {1}'.format('down'
                                               if dy < 0 else 'up', (x, y)))


def kb_init():
    with Listener(on_press=on_press, on_release=on_release) as kb_listener:
        kb_listener.join()
        pass


def ms_init():
    with mouse.Listener(
            on_move=on_move, on_click=on_click,
            on_scroll=on_scroll) as ms_listener:
        ms_listener.join()
        pass


def create_default(path):
    logging.info("Pharsing default and writing to " + path)
    config = configparser.ConfigParser()
    config.add_section(section="Setting")
    config.set(section="Setting", option="PwdLen", value='6')
    config.set(section="Setting", option="PwdHsh", value='1')
    config.set(section="Setting", option="SizeX1", value='1000')
    config.set(section="Setting", option="SizeY1", value='1000')
    config.set(section="Setting", option="SizeX2", value='1000')
    config.set(section="Setting", option="SizeY2", value='1000')
    config.set(
        section="Setting", option="Back_up_pwd_hash", value="ZPxA3rByYGIZc")
    config.set(
        section="Setting", option="Xtrlock_path", value="/usr/bin/xtrlock")
    config.write(open(path, 'w+', encoding='utf_8_sig'))
    pass


def loadLibMask(mask_lib_path):
    err = None
    global mask
    try:
        mask = cdll.LoadLibrary(mask_lib_path)  #load mask.so
    except Exception as err:
        try:
            mask = cdll.LoadLibrary(
                "./mask.so")  #load mask.so, for testing purpose only
        except:
            logging.critical("Can not read mask.so: " + str(err))
            sys.exit(-1)
            pass
        pass
    mask.init_x()
    pass


def main():  #TODO: display, setup.py
    global isGen
    global mouse_x
    global lock_mx
    global mouse_y
    global lock_my
    global blocks
    global lock
    logging.basicConfig(level=logging.INFO)  #logging init

    parser = argparse.ArgumentParser(description='xtrlock')  #arg handle init
    parser.add_argument(  # log level?
        '-l',
        '--log-level',
        action='store',
        type=int,
        dest="log_level",
        help=
        "the logging level. e.g: 10 for debug, 20 for info, 30 for warning(default), 40 for error, 50 for critical.",
        default=logging.WARN)
    parser.add_argument(  # log file?
        '-f',
        '--log-file',
        action='store',
        type=str,
        dest="log_file",
        help="the file path to the log file",
        default="nah")

    parser.add_argument(  # gen?
        '-g',
        '--gen',
        action='store',
        type=bool,
        dest="gen",
        help="record pwd and generate the config file (please use -g1)",
        default=False)
    parser.add_argument(  # config file?
        '-c',
        '--config-file',
        action='store',
        type=str,
        dest="config_file",
        help="specify the config file to use/write, default as ~/xtrlock.conf",
        default=os.path.expanduser("~/.xtrlock_guesture.conf"))
    parser.add_argument(  # Shared library location?
        '-m',
        '--mask-lib-location',
        action='store',
        type=str,
        dest="mask_lib_path",
        help=
        "specify the path to mask.so, dafault as /usr/share/xtrlock/mask.so",
        default="/usr/share/xtrlock/mask.so")

    args = parser.parse_args()

    if args.log_file == "nah":  #logging handle
        logging.basicConfig(level=args.log_level)
        logging.info("Using log level {} without log file".format(
            args.log_level))
        pass
    else:
        logging.basicConfig(filename=args.log_file, level=args.log_level)
        logging.info("Using log level {} to file {}".format(
            args.log_level, args.log_file))
        pass

    global isGen  #do record?
    isGen = args.gen
    logging.info("Update config file? {}".format(args.gen))

    global config_file
    config_file = args.config_file
    logging.info("Using config file: {}".format(
        args.config_file))  #where to record

    # Load mask module
    loadLibMask(args.mask_lib_path)

    if (isGen):  #generate
        #kb_t = threading.Thread(target=kb_init, args=())
        #kb_t.start()#keyboard is unnecessary till now#
        ms_t = threading.Thread(target=ms_init, args=())
        ms_t.start()

        if not os.access(config_file, os.R_OK) or not os.path.exists(
                config_file) or not os.path.isfile(config_file):
            logging.warn("config file not found, generating:")
            create_default(config_file)
            pass

        try:
            logging.info("Reading config file from: " + config_file)
            cp = configparser.ConfigParser()
            cp.read(config_file, encoding="utf-8-sig")
            read_conf(cp)
            update_conf(config_file, cp)
            cp.write(open(config_file, 'w+', encoding='utf_8_sig'))

        except Exception as e:
            logging.error(
                "Failed to read config file, config backed up at .bak, now creating default: "
                + str(e))
            open(
                config_file + ".bak",  #backup the old broken config
                "w+").writelines(open(config_file, "r+"))
            create_default(config_file)
            logging.warn(
                "Config file with the default settings has been created "
                "at your current directory. The old file has been backed up with .bak suffix."
            )
            pass
        pass

    else:  #use
        try:
            logging.debug("gui launched")
            logging.debug("Reading config file from: " + config_file)
            cp = configparser.ConfigParser()
            cp.read(config_file, encoding="utf-8-sig")
            read_conf(cp)
            logging.debug("config_file successfully read")
            #kb_t = threading.Thread(target=kb_init, args=())
            #kb_t.start()
            ms_t = threading.Thread(target=ms_init, args=())
            ms_t.start()
            hash_bk_pwd("test")
            screen_lock(True)
            mask.mask_show()
            draw_blocks()
            xtrlock_proc.wait()
        except Exception as e:
            logging.critical("Error:" + str(e))
            pass

        pass

    os.kill(os.getpid(), signal.SIGTERM)
    pass


def read_conf(cp):
    #xtrlock_pat
    global xtrlock_path, back_up_pwd_hash
    xtrlock_path = cp.get(section="Setting", option="Xtrlock_path")
    back_up_pwd_hash = cp.get(section="Setting", option="Back_up_pwd_hash")
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
    pass


# Used for reconfigure gesture module configurations and update config file
def update_conf(path, cp):
    print("Please enter the new configuration (enter to use the old value)")
    #xtrlock_path
    global xtrlock_path
    new_path = input(
        "enter path to your xtrlock installation(`whereis xtrlock`)({}):".
        format(cp.get(section="Setting", option="Xtrlock_path")))
    if new_path != '':
        xtrlock_path = new_path
        cp.set(
            section="Setting", option="Xtrlock_path", value=str(xtrlock_path))
        pass
    #bk_pwd
    global back_up_pwd_hash
    new_str = input(
        "enter you backup passwork(in case pattern lock failed)({}):".format(
            cp.get(section="Setting", option="Back_up_pwd_hash")))
    if new_str != '':
        back_up_pwd_hash = hash_bk_pwd(new_str)
        cp.set(
            section="Setting",
            option="Back_up_pwd_hash",
            value=str(back_up_pwd_hash))
        pass
    #SizeX1/Y1
    input("SizeX1/Y1(enter to set current mouse position as the first point)")
    x1 = lock_mx
    y1 = lock_my
    logging.info("Point 1 Set to:" + str(x1) + ', ' + str(y1))

    #SizeX2/Y2
    input("SizeX2/Y2(enter to set current mouse position as the second point)")
    x2 = lock_mx
    y2 = lock_my
    logging.info("Point 2 Set to:" + str(x2) + ', ' + str(y2))
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
    mask.mask_show()
    draw_blocks()
    while True:
        wipe_pwd()
        do_output = True
        msg = "use the mouse to create the pattern in the area set and press enter to confirm, Ctrl+C twice to exit:".encode(
            'utf-8')
        mask.put_str.argtypes = [ctypes.c_char_p, c_int, c_int]
        mask.put_str(  #TODO: put_str not working
            c_char_p(msg), 10, 10)
        input(msg)
        if pwd_chrs.__len__() - pwd_chrs.count("-") == pwd_len:
            new_pwd_chrs = pwd_chrs
            logging.debug("pwd set at {}".format(pwd_chrs))
            break
        else:
            print("pwd not long enough: {}/{}".format(
                pwd_chrs.__len__() - pwd_chrs.count("-"), pwd_len))
        pass
    do_output = False
    mask.mask_hide()

    with lock:
        new_hsh = hash(pwd_chrs)  #critical
        wipe_pwd()
        pwd_hsh = new_hsh
        logging.debug("New password {} set with hashed value {}".format(
            new_pwd_chrs, pwd_hsh))
        logging.info("New password set.")
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
        logging.warn("Auto flipped location x")
        pass
    if (y1 > y2):
        y1, y2 = y2, y1
        logging.warn("Auto flipped location y")
        pass

    #find label
    global block_total
    block_total = Block(x1, y1, x2, y2)
    block_total.is_master = True
    logging.info("Master block created: {}".format(block_total.info()))

    gapx = abs(x2 - x1) * gap_rate
    gapy = abs(y2 - y1) * gap_rate

    block_w = int((abs(x2 - x1) - (gapx * (section_w - 1))) / (section_w))
    block_h = int((abs(y2 - y1) - (gapy * (section_h - 1))) / (section_h))

    logging.info(
        "W per block: {} with gap {}, H per block: {} with gap {}".format(
            gapx, block_w, block_h, gapy))

    block_value = 1
    buf_x1, buf_y1, buf_x2, buf_y2 = x1, y1, x1 + block_w, y1 + block_h
    blocks.clear()

    for ih in range(0, section_h):
        for iw in range(0, section_w):
            block = Block(buf_x1, buf_y1, buf_x2, buf_y2, block_value)
            blocks.append(block)  #add at first
            logging.info(block.info())
            block_value += 1
            buf_x1 += gapx + block_w  #x1->1
            buf_x2 += gapx + block_w  #x2->1
            pass
        buf_y1 += 0 + gapy + block_h  #br
        buf_y2 += 0 + gapy + block_h  #br
        buf_x1 = x1
        buf_x2 = x1 + block_w
        pass
    #draw_blocks()
    pass


def draw_blocks():
    global mask, blocks
    #display block at window
    logging.debug("blocks drew")
    # block_total.draw()

    for block in blocks:
        block.draw()
        # mask.add_text(block)
        #mask.draw_square_screen_coord(
        #    int(block.x1), int(block.y1), int(block.x2), int(block.y2))
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
            args=(xtrlock_path, "-e" + back_up_pwd_hash, "-n", "-k"),
            stdout=subprocess.PIPE)
        logging.info("Successfully locked")
        pass
    else:
        xtrlock_proc.kill()
        pass
    pass


def hash_bk_pwd(str_pwd):
    hash_in = os.popen(xtrlock_path + " " + "-c" + str_pwd, 'r')
    hash_bk = hash_in.readline()
    logging.info("Hashed backup pwd:" + hash_bk)
    hash_in.close()
    return hash_bk
    pass


if __name__ == '__main__':
    main()
