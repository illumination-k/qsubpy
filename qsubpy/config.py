import os
import re
import toml
import subprocess

from typing import Dict, Optional, List

import logging

logger = logging.Logger(__name__)


def no_exist_msg(s: str) -> str:
    """return no exist s in config"""

    return f"{s} do not exist in qsubpy_config.toml"


class Resource:
    def __init__(self, config: Dict) -> None:
        self.resource_params: str = config["resource"]["header"].rstrip("\n")
        self.default_mem: str = config["resource"]["default_mem"]
        self.default_slot: str = config["resource"]["default_slot"]

    def _resource(self, mem: str = None, slot: str = None) -> str:
        if mem is None:
            mem = self.default_mem
        if slot is None:
            slot = self.default_slot
        return self.resource_params.replace("{mem}", str(mem)).replace(
            "{slot}", str(slot)
        )


class SingularityConfig:
    def __init__(self, config: Dict) -> None:
        singularity = config.get("singularity")
        if singularity is None:
            logger.warn(no_exist_msg("singularity"))
            self.singularity_image_root = None
            self.singularity_default_ext = None
        else:
            self.singularity_image_root = singularity.get("image_root")
            self.singularity_default_ext = singularity.get("default_ext")

    def singularity_image(self, image: str, root: Optional[str]) -> str:
        if self.singularity_default_ext is None:
            logger.warn(f"singularity default ext is not set in config.toml, so use image name: {image} directly!")
        else:
            if not image.endswith(self.singularity_default_ext):
                image += f".{self.singularity_default_ext}"

        # image is abspath
        if image.startswith(os.path.sep) or image.startswith("~"):
            return image

        # overwrite root information
        if root is not None:
            return os.path.join(root, image)

        # use default root information
        if self.singularity_image_root is not None:
            return os.path.join(self.singularity_image_root, image)

        # return image only
        return image


#!TODO: add log path
#!TODO: add singularity
class Config:
    def __init__(self, config: dict):
        self.header: str = config["scripts"]["header"].rstrip("\n")
        self.body: str = config["scripts"]["body"].rstrip("\n")

        # Reource
        self.resources = Resource(config)

        # array job
        self.array_job_id: Optional[str] = None
        if config["arrayjob"]["id"].startswith("$"):
            self.array_job_id = config["arrayjob"]["id"]
        else:
            self.array_job_id = "$" + config["arrayjob"]["id"]
        self.array_params: str = config["arrayjob"]["header"].rstrip("\n")

        # qsub option
        options = config.get("options")
        if options is None:
            logger.warn(no_exist_msg("Options"))
            self.sync_options = None
            self.ord_options = None
        else:
            self.sync_options: Optional[List[str]] = options.get("sync")
            self.ord_options: Optional[List[str]] = options.get("order")

        # jid re
        jid = config.get("jid")
        if jid is None:
            logger.warn(no_exist_msg("jid"))
            self.jid_re = None
        else:
            self.jid_re: Optional[re.Pattern] = re.compile(config["jid"].get("re"))

        # common variables
        common_variables = config.get("common_variables")
        if common_variables is None:
            self.common_variables = {}
        else:
            self.common_variables = common_variables

        # singularity
        self.singularity_config = SingularityConfig(config)

    def resource(self, mem: Optional[str] = None, slot: Optional[str] = None) -> str:
        return self.resources._resource(mem=mem, slot=slot)

    def array_header_with_cmd(self, command: str) -> tuple:
        length = self.bash_array_len(command)
        array_header = (
            self.array_params.replace("{start}", "1")
            .replace("{end}", str(length))
            .replace("{step}", "1")
        )
        array = f"array=($({command}))"
        # like following
        # elem=${array[$(($SGE_TASK_ID-1))]}
        elem = "elem=${array[$((" + self.array_job_id + "-1))]}"
        return array_header, "\n".join([array, elem])

    def sync_qsub_command(self) -> list:
        return ["qsub"] + self.sync_options

    def ord_qsub_command(self, jid: str) -> list:
        cmd = ["qsub"]
        for s in self.ord_options:
            if "{JID}" in s:
                cmd.append(s.replace("{JID}", jid))
            else:
                cmd.append(s)
        return cmd

    def make_common_variables_list(self):
        if self.common_variables == {}:
            return []

        ret = []
        for k, v in self.common_variables.items():
            ret.append(k + "=" + "\"" + str(v) + "\"")
        return ret

    def common_variables_1linear(self) -> str:
        l = self.make_common_variables_list()
        if len(l) == 0:
            return ""

        ret_command = ""
        ret_command = " && ".join(l)
        ret_command += " && "
        return ret_command

    def make_common_variables_params(self):
        return "\n".join(self.make_common_variables_list())

    def bash_array_len(self, command: str) -> int:
        """array length of bash
        Args:
            command (str): command
        Returns:
            int: length of array in bash

        >>> bash_array_len("echo 'a b'")
        2
        """
        len_command = self.common_variables_1linear()

        len_command += " ".join([f"t=($({command}))", "&&", "echo ${#t[@]}"])

        logger.debug(f"len_command: {len_command}")
        proc = subprocess.run(
            len_command, shell=True, capture_output=True, executable="/bin/bash"
        )
        try:
            ret = int(proc.stdout)
        except:
            logger.error(f"{len_command} results cannot to convert integer")
            raise ValueError(
                "Invalid literal for int(). Please check your array command!"
            )
        return ret

    def __str__(self):
        ret = ["-" * 20]
        ret.append("config_path: " + get_default_config_path())


def get_default_config_path() -> str:
    path = os.environ.get("QSUBPY_CONFIG")
    if path is None:
        home = os.environ["HOME"]
        path = os.path.join(home, ".config", "qsubpy_config.toml")
    return path


def read_config(path: str = None) -> Config:
    path = get_default_config_path()
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

[singularity]
image_root = "~/singularity_img"
default_ext = "sif"
'''


def generate_default_config():
    path = get_default_config_path()

    if os.path.exists(path):
        return

    with open(path, "w") as f:
        f.write(SHIROKANE_CONFIG)
