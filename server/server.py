#!/usr/bin/env python3
# This is the server program used to control the trigger and deactivation of BetterXTrLock.
# It served to make sure the actual screen lock process will not own a high privilege
# while its trigger could still enjoy higher level privileges like triggering a screen lock
# when certain file is accessed.

import threading
import sys, os
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
import socket
import time
import timeout_decorator

global sock
global connections
connections = []


class Connection:
    connection_id = None
    sock = None

    def __init__(self, conn):
        self.sock = conn
        self.connection_id = hash(os.times()[0])
        self.register()
        logging.debug("New connection with id: {}".format(self.connection_id))

    def register(self):
        global connections
        connections.append(self)

    def unregister(self):
        global connections
        try:
            self.sock.close()
            connections.remove(self)
        except Exception as e:
            logging.warn("Exception in unregister connection {}: {}".format(
                self.connection_id, str(e)))


def init_socket(args):
    global sock
    server_address = args.server_socket_address
    if os.path.exists(server_address):
        logging.warn(
            "Server socket file {} already exists, overriding.".format(
                server_address))
        os.remove(server_address)
    logging.info("Listening on: {}".format(server_address))
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen(0)
    pass


def logging_init(args):
    if args.log_file == "nah":  #logging handle
        logging.basicConfig(level=args.verbose_level)
        logging.info("Using log level {} without log file".format(
            args.verbose_level))
        pass
    else:
        logging.basicConfig(filename=args.log_file, level=args.verbose_level)
        logging.info("Using log level {} to file {}".format(
            args.verbose_level, args.log_file))
        pass
    pass


def config_init(args):
    global cmds, user
    cmds = args.lock_cmd.split(":")
    user = args.user
    pass


# @timeout_decorator.timeout(1)
def connection_handler(conn):
    try:
        logging.info("Connection established, waiting for request")
        conn.sock.recv(1)
        logging.info("Lock request received")
        global user, cmds
        trigger_screen_lock(user, cmds[0])
        pass
    except Exception as e:
        logging.error("Error in connection handle: {}".format(str(e)))
        pass
    finally:
        conn.unregister()
        sys.exit(-1)
        pass
    sys.exit(0)


def trigger_screen_lock(usr, cmd):
    logging.info("As |{}| running cmd |{}|".format(usr, cmd))
    os.system("sudo -u " + usr + " " + cmd)
    # os.system("sudo -u d0048 xtrlock -p 123")
    pass


def main():
    logging.basicConfig(level=logging.INFO)

    # TODO: test client
    parser = argparse.ArgumentParser(description='xtrlock')
    parser.add_argument(  # log level
        '-v',
        '--verbose-level',
        action='store',
        type=int,
        dest="verbose_level",
        help=
        "the logging level. e.g: 10 for debug, 20 for info, 30 for warning(default), 40 for error, 50 for critical, default as INFO(20).",
        default=logging.WARN)
    parser.add_argument(  # log file
        '-f',
        '--log-file',
        action='store',
        type=str,
        dest="log_file",
        help="the file path to the log file",
        default="nah")
    parser.add_argument(  # Command to execute
        '-l',
        '--lock-cmd',
        action='store',
        type=str,
        dest="lock_cmd",
        help=
        "The command used to lock screen, which could be set to trigger programs like xscreensaver other than xtrlock, default as `xtrlock -l`, separate multiple command with :",
        default="xtrlock -p 123")
    parser.add_argument(  # User to run as
        '-u',
        '--user',
        action='store',
        type=str,
        dest="user",
        help=
        "The user used to execute the lock command, it is recommended to create a new user with no permissions but to the screen lock utility, for safety. Default as current user",
        default=os.environ["USER"])
    parser.add_argument(  # Server file to listen
        '-s',
        '--server-socket-location',
        action='store',
        type=str,
        dest="server_socket_address",
        help=
        "The socket file used for other triggers to request a lock/unlock function, default as /tmp/xtrlock_server_trigger",
        default="/tmp/xtrlock_server_trigger")
    args = parser.parse_args()

    logging_init(args)
    config_init(args)

    # =============== Arg Handling Complete ==========================

    global sock
    try:
        init_socket(args)
    except Exception as e:
        print("Failed to init socket: " + str(e))
        sock.close()
        pass

    # TODO: Timeout, Threading
    global running, connections
    running = True
    while running:
        s, addr = sock.accept()
        conn = Connection(s)
        handle = threading.Thread(target=connection_handler, args=([conn]))
        handle.start()
        pass

    sock.close()

    pass


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


def hash(string):
    return hashlib.md5(
        str(string).encode("utf-8")).hexdigest()  #.encode('utf-8').hexdigest()


if __name__ == '__main__':
    main()
