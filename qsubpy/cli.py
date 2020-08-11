import argparse
import subprocess
import sys
import os

import logging
logger = logging.getLogger(__name__)

from qsubpy import run
from qsubpy import generate_yaml

# set color logger
mapping = {
    "TRACE": "[ trace ]",
    "DEBUG": "[ \x1b[0;36mdebug\x1b[0m ]",
    "INFO": "[ \x1b[0;32minfo\x1b[0m ]",
    "WARNING": "[ \x1b[0;33mwarn\x1b[0m ]",
    "WARN": "[ \x1b[0;33mwarn\x1b[0m ]",
    "ERROR": "\x1b[0;31m[ error ]\x1b[0m",
    "ALERT": "\x1b[0;37;41m[ alert ]\x1b[0m",
    "CRITICAL": "\x1b[0;37;41m[ alert ]\x1b[0m",
}

class ColorfulHandler(logging.StreamHandler):
    def emit(self, record):
        record.levelname = mapping[record.levelname]
        super().emit(record)


def __main__():
    parser = argparse.ArgumentParser()
    
    # main parsers
    parser.add_argument("-c", "--command", type=str, default=None)
    parser.add_argument("-f", "--file", type=str, default=None)
    parser.add_argument("-s", "--setting", type=str, default=None)
    parser.add_argument("--mem", type=str, default="4G")
    parser.add_argument("--slot", type=str, default="1")
    parser.add_argument("-n", "--name", type=str, default=None)
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--ls", type=str, default=None, help="pattern of ls, translate to array job. You can use file variable in command or the sh file.")
    parser.add_argument("--dry_run", action="store_true", help="Only make sh files for qsub. not run.")
    parser.add_argument("--log_level", default="info", choices=["error", "warning", "warn", "info", "debug"])

    # subparsers
    subparsers = parser.add_subparsers()
    
    # to generate setting file easily
    ## args
    generate_yaml_parser = subparsers.add_parser("generate_settings", help="generate settings file")
    generate_yaml_parser.add_argument("-o", "--output", type=str, required=True)
    generate_yaml_parser.add_argument("--stage_num", type=int, default=3)
    generate_yaml_parser.add_argument("--mem", type=str, default="4G", help="set default mem")
    generate_yaml_parser.add_argument("--slot", type=str, default="1", help="set default slot")
    ##
    generate_yaml_parser.set_defaults(handler=generate_yaml.parse_args)
    
    args = parser.parse_args()

    if args.command is not None:
        run.command_mode(args.command, args.mem, args.slot, args.name, args.ls, args.dry_run)
        sys.exit(0)
    
    if args.file is not None:
        if not os.path.exists(args.file):
            raise IOError(f'{args.file} does not exists!')
        run.file_mode(args.file, args.mem, args.slot, args.name, args.ls, args.dry_run)
        sys.exit(0)

    if args.setting is not None:
        run.setting_mode(args.setting)
        sys.exit(0)
    
    logger.error("--command, --settings or --file is need")
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    __main__()