from pynput.keyboard import *
from pynput import mouse
import threading
import multiprocessing
import hashlib
import argparse
import configparser

global trigger
global isGen
#global configFile
triggered = False


def on_press(key):
    print('{0} pressed'.format(key))

    if (str(key).startswith(trigger)):
        print("triggered")
        triggered = True
        pass
    pass


def on_release(key):
    print('{0} release'.format(key))
    if (str(key).startswith(trigger)):
        print("detriggered")
        triggered = False
        pass


def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))
    ohash = hashlib.md5((str(x) + str(y)).encode('utf-8')).hexdigest()
    print(str(ohash))


def on_click(x, y, button, pressed):
    print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
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
    #TODO: create default file
    print("Pharsing default and writing to " + path)
    config = configparser.ConfigParser()
    config.add_section(section="Setting")
    config.set(section="Setting", option="Trigger", value='a')
    config.set(section="Setting", option="Pwd", value='112233')
    config.set(section="Setting", option="SizeH", value='1000')
    config.set(section="Setting", option="SizeW", value='1000')
    config.write(open(path, 'w+', encoding='utf_8_sig'))
    pass


def main():
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
    print("generate file: "+str(isGen))

    print(args.config_file)  #where to record
    config_file = args.config_file
    print(config_file)

    if not os.access("myfile", os.R_OK) or not os.path.exists(
            config_file) or not os.path.isfile(config_file):
        create_default(config_file)
        pass

    try:
        print("Reading config file from: "+config_file)
        cp = configparser.ConfigParser()
        cp.read(config_file, encoding="utf-8-sig")
    except Exception as e:
        print(
            "Failed to read config file, config backed up at .bak, now creating default: "
            + str(e))
        open(config_file + ".bak", "w+").writelines(open(config_file,"r+"))
        create_default(config_file)

    kb_proc = multiprocessing.Process(target=kb_init, args=())
    kb_proc.start()
    ms_proc = multiprocessing.Process(target=ms_init, args=())
    ms_proc.start()


main()
