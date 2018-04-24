#!/usr/bin/env python3

import pyinotify
import os, sys
from triggerlib import *
import logging
import time

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
        '-t',
        '--time-in-second',
        action='store',
        type=int,
        dest="sec",
        help="The time in seconds before locking, default 10",
        default=10)
    args = parser.parse_args()
    logging.basicConfig(level=args.verbose_level)
    addr = args.server_address
    count = args.sec
    # =====================args handling complete====================================

    logging.info("Starting countdown in: " + str(count))

    time.sleep(args.sec)
    trigger(addr)
    pass


if __name__ == '__main__':
    main()
