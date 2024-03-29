import logging
from typing import List, Dict, Optional
from argparse import ArgumentParser


logger = logging.getLogger(__name__)


def sanitize_dict_key(d: Dict) -> Dict:
    def change_dict_key(old_key, new_key, default_value=None):
        nonlocal d
        d[new_key] = d.pop(old_key, default_value)

    keys = list(d.keys())
    for key in keys:
        new_key = key.rstrip("\n").replace("-", "_")
        change_dict_key(old_key=key, new_key=new_key)

    return d


def add_default_args(parser: ArgumentParser, handler) -> ArgumentParser:
    parser.add_argument("--mem", type=str, default="4G", help="default memory")
    parser.add_argument("--slot", type=str, default="1", help="default slots")
    parser.add_argument("-n", "--name", type=str, default=None, help="job name")

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


def make_uuid() -> str:
    """make uuid4
    Returns:
        str: uuid4
    """
    import uuid

    return "tmp_" + str(uuid.uuid4())


def read_sh(path: str):
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
    mem: Optional[str],
    slot: Optional[str],
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
    from qsubpy.config import read_config

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


def make_singularity_command(
    command: List[str], singularity_img: str, bind_dirs: Optional[List[str]] = None
) -> str:
    """make singularity command from the raw command
    singularity exec -B binddir1 -B binddir2 singularity_img cmd
    """

    ret = ["singularity", "exec"]

    if bind_dirs is not None:
        for bind_dir in bind_dirs:
            ret += ["-B", bind_dir]

    ret += [singularity_img] + command
    return " ".join(ret)
