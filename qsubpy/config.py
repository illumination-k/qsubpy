import os
import re
import toml
import subprocess

import logging

logger = logging.Logger(__name__)


def bash_array_len(command: str) -> int:
    """array length of bash
    Args:
        command (str): command
    Returns:
        int: length of array in bash

    >>> bash_array_len("echo 'a b'")
    2
    """
    len_command = " ".join([f"t=($({command}))", "&&", "echo ${#t[@]}"])
    logger.debug(f"len_command: {len_command}")
    proc = subprocess.run(
        len_command, shell=True, capture_output=True, executable="/bin/bash"
    )
    try:
        ret = int(proc.stdout)
    except:
        logger.error(f"{len_command} results cannot to convert integer")
        raise ValueError("Invalid literal for int()")
    return ret


class Config:
    def __init__(self, config: dict):
        self.header: str = config["scripts"]["header"].rstrip("\n")
        self.body: str = config["scripts"]["body"].rstrip("\n")

        # Reource
        self.resource_params: str = config["resource"]["header"].rstrip("\n")
        self.default_mem = config["resource"]["default_mem"]
        self.default_slot = config["resource"]["default_slot"]

        # array job
        self.array_job_id: str = None
        if config["arrayjob"]["id"].startswith("$"):
            self.array_job_id = config["arrayjob"]["id"]
        else:
            self.array_job_id = "$" + config["arrayjob"]["id"]
        self.array_params: str = config["arrayjob"]["header"].rstrip("\n")

        # qsub option
        self.sync_options: "list[str]" = config["options"]["sync"]
        self.ord_options: "list[str]" = config["options"]["order"]

        # jid re
        self.jid_re = re.compile(config["jid"]["re"])

    def resource(self, mem: str = None, slot: str = None) -> str:
        if mem is None:
            mem = self.default_mem
        if slot is None:
            slot = self.default_slot
        return self.resource_params.replace("{mem}", str(mem)).replace(
            "{slot}", str(slot)
        )

    def array_header_with_cmd(self, command: str) -> tuple:
        length = bash_array_len(command)
        array_header = (
            self.array_params.replace("{start}", "1")
            .replace("{end}", str(length))
            .replace("{step}", "1")
        )
        array = f"array=($({command}))"
        # like following
        # elem=${array[$(($SEG_TASK_ID-1))]}
        elem = "elem=${array[$((" + self.array_job_id + "-1))]}"
        return array_header, "\n".join([array, elem])

    def sync_qsub_command(self) -> list:
        return ["qsub"] + self.sync_options

    def ord_qsub_command(self, jid: str) -> list:
        cmd = ["qsub"]
        for s in self.ord_options:
            if s == "{JID}":
                cmd.append(jid)
            else:
                cmd.append(s)
        return cmd


def read_config(path: str = None) -> Config:
    path = os.environ.get("QSUBPY_CONFIG")
    if path is None:
        home = os.environ.get("HOME")
        path = os.path.join(home, ".config", "qsubpy_config.toml")
    config_dict = toml.load(open(path))

    return Config(config_dict)


SHIROKANE_CONFIG = '''
[scripts]
header = """
#!/bin/bash
#$ -S /bin/bash
#$ -cwd
"""
body = """
source ~/.bashrc
source ~/.bash_profile
set -eu
"""

[resource]
default_mem = "4G"
default_slot = "1"
header = """
#$ -l s_vmem={mem} -l mem_req={mem}
#$ -pe def_slot {slot}
"""

[arrayjob]
id = "SGE_TASK_ID"
header = "#$ -t {start}-{end}:{step}"

[options]
sync = ["-sync", "y"]
order = ["-hold_jid", "{JID}"]

[jid]
"Your (job|job-array) (?P<jid>\\d{8})"
'''


def generate_defulat_config():
    path = os.environ.get("QSUBPY_CONFIG")
    home = os.environ.get("HOME")
    if path is None:
        path = f"{home}/.config/qsubpy_config.toml"

    if os.path.exists(path):
        return

    if not os.path.exists(os.path.join(home, ".config")):
        os.makedirs(os.path.join(home, "config"))

    with open(path, "w") as f:
        f.write(SHIROKANE_CONFIG)
