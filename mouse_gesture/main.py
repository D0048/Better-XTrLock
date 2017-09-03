from pynput.keyboard import *
from pynput import mouse
import threading
import multiprocessing
import hashlib


def on_press(key):
    print('{0} pressed'.format(key))


def on_release(key):
    print('{0} release'.format(key))
    if key == Key.esc:
        # Stop listener
        return False


def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))
    ohash=hashlib.md5((str(x) + str(y)).encode('utf-8')).hexdigest()
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


def main():
    kb_proc = multiprocessing.Process(target=kb_init, args=())
    kb_proc.start()
    ms_proc = multiprocessing.Process(target=ms_init, args=())
    ms_proc.start()
    print("test")


main()
