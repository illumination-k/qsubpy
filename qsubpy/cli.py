import argparse
import subprocess
import sys

import logging
logger = logging.getLogger(__name__)

from qsubpy import run

def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--command", type=str, default=None)
    parser.add_argument("-f", "--file", type=str, default=None)
    parser.add_argument("-s", "--setting", type=str, default=None)
    parser.add_argument("-m", "--mem", type=str, default="4G")
    parser.add_argument("-s", "--slot", type=str, default="1")
    parser.add_argument("-n", "--name", type=str, default=None)
    parser.add_argument("--ls", type=str, default=None, help="pattern of ls, translate to array job. You can use file variable in command or the sh file.")
    args = parser.parse_args()

    if args.command is not None:
        run.command_mode(args.command, args.mem, args.slot, args.name, args.ls)
        sys.exit(0)
    
    if args.file is not None:
        run.file_mode(args.file, args.mem, args.slot, args.name, args.ls)
        sys.exit(0)

    if args.setting is not None:
        sys.exit(0)
    
    logger.error("--command, --settings or --file is need")
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    __main__()