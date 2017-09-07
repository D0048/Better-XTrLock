from pynput.keyboard import *
from pynput import mouse
import threading
import multiprocessing
from multiprocessing import *
import hashlib
import argparse
import configparser

global trigger
global isGen
global mouse_x
global lock_mx
global mouse_y
global lock_my
global blocks
mouse_x = 1
mouse_y = 1
triggered = False

#lock_mx = Lock()
#counter = Value('i', 0) # int type，相当于java里面的原子变量
'''
block0 = Block()
block1 = Block()
block2 = Block()
block3 = Block()
block4 = Block()
block5 = Block()
block6 = Block()
block7 = Block()
block8 = Block()
block9 = Block()
block_total = Block()
'''


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
        self.value = value
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
    global triggered

    if (str(key).startswith(trigger)):
        print("triggered")
        triggered = True
        pass
    pass


def on_release(key):
    #print('{0} release'.format(key))
    global triggered
    if (str(key).startswith(trigger)):
        print("detriggered")
        triggered = False
        pass


def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))
    #ohash = hashlib.md5((str(x) + str(y)).encode('utf-8')).hexdigest()
    #print(str(ohash))
    global lock_mx, lock_my
    global blocks, block_total
    lock_mx = x
    lock_my = y
    if block_total.check(x, y):
        for b in blocks:
            if b.check(x, y) and b.value != "nah":
                print(b.value)
                pass
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
    config.set(section="Setting", option="Trigger", value='a')
    config.set(section="Setting", option="Pwd", value='112233')
    config.set(section="Setting", option="SizeX1", value='1000')
    config.set(section="Setting", option="SizeY1", value='1000')
    config.set(section="Setting", option="SizeX2", value='1000')
    config.set(section="Setting", option="SizeY2", value='1000')
    config.write(open(path, 'w+', encoding='utf_8_sig'))
    pass


def main():  #TODO:record, hash, display
    global trigger
    global isGen
    global mouse_x
    global lock_mx
    global mouse_y
    global lock_my
    global blocks
    parser = argparse.ArgumentParser(description='xtrlock')
    parser.add_argument(
        '-t',
        '--trigger',
        action='store',
        type=str,
        dest="trigger",
        help="trigger key of the action",
        default="a")
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

    print(args.trigger)  #is trigger?
    global trigger
    trigger = '\'' + args.trigger
    print("Trigger:" + trigger)

    print(args.gen)  #do record?
    global isGen
    isGen = args.gen
    print("generate file: " + str(isGen))

    print(args.config_file)  #where to record
    global config_file
    config_file = args.config_file
    print(config_file)

    if (isGen):
        #kb_proc = multiprocessing.Process(target=kb_init, args=())
        #kb_proc.start()
        #ms_proc = multiprocessing.Process(target=ms_init, args=())
        #ms_proc.start()
        kb_t = threading.Thread(target=kb_init, args=())
        #kb_t.setDaemon(True)
        kb_t.start()
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


def update_conf(path, cp):
    #trigger
    new_trigger = input("SizeH(" + cp.get("Setting", "Trigger", raw=True) +
                        "):")
    print(str(new_trigger))
    if (new_trigger != ''): cp.set("Setting", "Trigger", new_trigger[0])

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
    cp.set("Setting", "SizeX1", str(x1))
    cp.set("Setting", "SizeX2", str(x2))
    cp.set("Setting", "SizeY1", str(y1))
    cp.set("Setting", "SizeY2", str(y2))
    update_blocks(x1, y1, x2, y2)
    pass


def update_blocks(x1, y1, x2, y2, section_w=3, section_h=3, gap_rate=0.1):
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

    block_w = int((abs(x2 - x1) - (gapx * (section_w - 1))) /
                  (section_w))  #TODO:super huge +/- value
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

    #TODO: cal blocks and set to global

    pass


main()
