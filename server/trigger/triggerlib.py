#!/usr/bin/env python3
# A lib file for triggers to activate a lock

import threading
import sys, os
import multiprocessing
from multiprocessing import *
from ctypes import *
import argparse
import configparser
import signal
import subprocess
import logging
import socket

default_addr = "/tmp/xtrlock_server_trigger"
'''
Notice: Use a None addr to use default address
'''


def trigger(addr):
    # TODO: Timeout, Threading
    if addr == None:
        addr = default_addr
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.sendall(bytes(1))
    logging.info("Request sent to: {}".format(addr))
    sock.close()
    pass


def main():
    print("testing on default server location....: " + default_addr)
    addr = default_addr
    trigger(addr)


if __name__ == '__main__':
    main()
