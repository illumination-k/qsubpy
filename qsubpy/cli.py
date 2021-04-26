import argparse
import subprocess
import sys
import os

import logging

logger = logging.getLogger(__name__)

from qsubpy import run

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
    parser = argparse.ArgumentParser(
        description="wrapper for qsub of UGE. easy to use array job and build workflow."
    )

    # main parsers
    parser.add_argument(
        "-c", "--command", type=str, default=None, help="run qusbpy with command mode"
    )
    parser.add_argument(
        "-f", "--file", type=str, default=None, help="run qsubpy with file mode"
    )
    parser.add_argument(
        "-s", "--setting", type=str, default=None, help="run qsubpy with settings mode"
    )
    parser.add_argument("--mem", type=str, default="4G", help="default memory")
    parser.add_argument("--slot", type=str, default="1", help="default slots")
    parser.add_argument("-n", "--name", type=str, default=None, help="job name")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument(
        "--ls",
        type=str,
        default=None,
        help="pattern of ls, translate to array job. You can use elem variable in command or the sh file.",
    )
    parser.add_argument(
        "--array_cmd",
        type=str,
        default=None,
        help="command for array job. You can use elem variable in command or the sh file.",
    )
    parser.add_argument(
        "--dry_run", action="store_true", help="Only make sh files for qsub. not run."
    )
    parser.add_argument(
        "--log_level",
        default="info",
        choices=["error", "warning", "warn", "info", "debug"],
        help="set log level",
    )

    # subparsers
    subparsers = parser.add_subparsers()

    # cmd, file and settings by subparsers

    args = parser.parse_args()

    # set log level
    if args.log_level == "error":
        log_level = logging.ERROR
    elif args.log_level == "warning":
        log_level = logging.WARNING
    elif args.log_level == "warn":
        log_level = logging.WARN
    elif args.log_level == "info":
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    # set logger
    logging.basicConfig(handlers=[ColorfulHandler()], level=log_level)

    if args.command is not None:
        run.command_mode(args)
        sys.exit(0)

    if args.file is not None:
        if not os.path.exists(args.file):
            raise IOError(f"{args.file} does not exists!")
        run.file_mode(args.file, args.mem, args.slot, args.name, args.ls, args.dry_run)
        sys.exit(0)

    if args.setting is not None:
        run.setting_mode(args.setting, args.dry_run)
        sys.exit(0)

    # run handler
    if hasattr(args, "handler"):
        args.handler(args)

    logger.error("--command, --settings or --file is need")
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    __main__()
