#!/usr/bin/env python3

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


def main():
    # TODO: Timeout, Threading
    running = True
    addr = "/tmp/xtrlock_server_trigger"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.sendall(bytes(1000))
    print("sent")
    sock.close()
    pass


if __name__ == '__main__':
    main()
