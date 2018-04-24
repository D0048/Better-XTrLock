#!/usr/bin/env python3

import pyinotify
import os, sys
from triggerlib import *
import logging


class LockHandle(pyinotify.ProcessEvent):
    def process_default(self, e):
        trigger(addr)
        pass

addr = None


def main():
    parser = argparse.ArgumentParser(description='xtrlock-on-file-change')
    parser.add_argument(  # log level
        '-v',
        '--verbose-level',
        action='store',
        type=int,
        dest="verbose_level",
        help=
        "the logging level. e.g: 10 for debug, 20 for info, 30 for warning(default), 40 for error, 50 for critical, default as INFO(20).",
        default=logging.WARN)
    parser.add_argument(  # server address
        '-s',
        '--server-address',
        action='store',
        type=str,
        dest="server_address",
        help="The server address, default: " + default_addr,
        default=None)
    parser.add_argument(  # file to watch
        '-f',
        '--file-to-watch',
        action='store',
        type=str,
        dest="file2watch",
        help="The file to watch, default: ./",
        default='./')
    args = parser.parse_args()
    logging.basicConfig(level=args.verbose_level)
    addr = args.server_address
    # =====================args handling complete====================================

    logging.info("Starting to watch: " + args.file2watch)
    watchManager = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(watchManager, LockHandle())
    watchManager.add_watch(args.file2watch, pyinotify.IN_CLOSE_WRITE)
    notifier.loop()
    pass

if __name__ == '__main__':
    main()
