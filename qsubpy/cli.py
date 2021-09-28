import argparse
import sys

import logging

logger = logging.getLogger(__name__)

from qsubpy import run
from qsubpy.utils import add_default_args
from qsubpy.validator import CommonVariableValidator
from qsubpy.config import generate_default_config

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


def command_mode_handler(args: argparse.Namespace):
    run.command_mode(args)


def file_mode_handler(args: argparse.Namespace):
    run.file_mode(args)


def workflow_mode_handler(args: argparse.Namespace):
    run.workflow_mode(args)


def __main__():
    parser = argparse.ArgumentParser(
        description="wrapper for qsub. Easy to use array job and build workflow."
    )

    # subparsers
    subparsers = parser.add_subparsers()

    # cmd
    cmd_parser = subparsers.add_parser(
        "command", aliases=["cmd", "c"], help="run qusbpy with command mode"
    )
    cmd_parser.add_argument(
        "command",
        metavar="Command",
        type=str,
        help="command you would like to run with qsub",
    )
    cmd_parser.add_argument(
        "--ls",
        type=str,
        default=None,
        help="pattern of ls, translate to array job. You can use elem variable in command or the sh file.",
    )
    cmd_parser.add_argument(
        "--array_cmd",
        type=str,
        default=None,
        help="command for array job. You can use elem variable in command or the sh file.",
    )
    add_default_args(cmd_parser, handler=command_mode_handler)

    # file
    file_parser = subparsers.add_parser(
        "file", aliases=["f"], help="run qsubpy with file mode"
    )
    file_parser.add_argument(
        "--ls",
        type=str,
        default=None,
        help="pattern of ls, translate to array job. You can use elem variable in command or the sh file.",
    )
    file_parser.add_argument(
        "--array_cmd",
        type=str,
        default=None,
        help="command for array job. You can use elem variable in command or the sh file.",
    )
    file_parser.add_argument(
        "file",
        metavar="Script File Path",
        type=str,
        help="File you would like to run with qsub",
    )
    add_default_args(file_parser, handler=file_mode_handler)

    # workflow
    workflow_parser = subparsers.add_parser(
        "workflow",
        aliases=["w", "setting", "settings", "s"],
        help="run qsubpy with workflow (setting) mode",
    )
    workflow_parser.add_argument(
        "workflow",
        metavar="Workflow Yaml Path",
        type=str,
        help="Workflow yaml you would like to run with qsub",
    )
    workflow_parser.add_argument(
        "-cv", "--common_variables", type=str, nargs="*", metavar="", default=[], choices=CommonVariableValidator()
    )
    add_default_args(workflow_parser, handler=workflow_mode_handler)

    args = parser.parse_args()
    logger.debug(args)

    generate_default_config()
    # set log level
    if hasattr(args, "log_level"):
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
    else:
        log_level = logging.INFO

    # set logger
    logging.basicConfig(handlers=[ColorfulHandler()], level=log_level)

    # run handler
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    __main__()
