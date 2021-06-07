import logging
from typing import Optional
from argparse import ArgumentParser


logger = logging.getLogger(__name__)


def add_default_args(parser: ArgumentParser, handler) -> ArgumentParser:
    parser.add_argument("--mem", type=str, default="4G", help="default memory")
    parser.add_argument("--slot", type=str, default="1", help="default slots")
    parser.add_argument("-n", "--name", type=str, default=None, help="job name")

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

    parser.set_defaults(handler=handler)

    return parser



def make_uuid():
    """make uuid4
    Returns:
        str: uuid4
    """
    import uuid

    return "tmp_" + str(uuid.uuid4())


def read_sh(path):
    """
    read a sh file. skip comment, shebang and qsub params.
    Args:
        path (str): path to the sh file
    Returns:
        list: list of lines of the sh file without comment, shebang and qsub params.
    """
    lines = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            lines.append(line.rstrip("\n"))
    return lines


def make_sh_file(
    cmd: list,
    mem: str,
    slot: str,
    name: Optional[str],
    ls_pattern: str = None,
    array_command: str = None,
    chunks=None,
    common_variables=None,
) -> str:
    """
    make sh file with qsub options. return generated file name.

    Args:
        cmd (list): command list
        mem (str): required memory, eg., 4G
        slot (str): required slot, eg., 1
        name (str): job name
        ls_pattern (str): mimic ls eg., /path/to/*.py
        common_variables (dict): common variable in bash script.
    Returns:
        str: generated file name
    """
    from qsubpy.templates import Template
    from qsubpy.config import read_config, generate_defulat_config

    generate_defulat_config()
    config = read_config()
    if common_variables is not None:
        config.common_variables.update(common_variables)

    template = Template(config)

    if ls_pattern is not None and array_command is not None:
        raise ValueError("You use only one of ls or array_command")

    if ls_pattern is not None and array_command is None:
        array_command = " ".join(["ls", ls_pattern])

    script = template.make_templates(
        array_command=array_command,
        mem=mem,
        slot=slot,
    )

    script += cmd

    if name is None:
        name = make_uuid()
    if not name.endswith(".sh"):
        name += ".sh"

    with open(name, "w") as f:
        f.write("\n".join(script))

    return name
