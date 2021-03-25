import toml
import subprocess

def bash_array_len(command: str) -> int:
    """array length of bash
    Args:
        command (str): command
    Returns:
        int: length of array in bash
    
    >>> bash_array_len("echo 'a b'")
    2
    """
    len_command = " ".join([f't=($({command}))', "&&", "echo ${#t[@]}"])
    proc = subprocess.run(len_command, shell=True, capture_output=True, executable="/bin/bash")
    return int(proc.stdout)

class Config:
    def __init__(self, config: dict):
        self.header: str = config["scripts"]["header"].rstrip("\n")
        self.body: str = config["scripts"]["body"].rstrip("\n")
        self.resource_params: str = config["resource"]["header"].rstrip("\n")
        self.default_mem = config["resource"]["default_mem"]
        self.default_slot = config["resource"]["default_slot"]
        self.array_job_id: str = None
        if config["arrayjob"]["id"].startswith("$"):
            self.array_job_id = config["arrayjob"]["id"]
        else:
            self.array_job_id = "$" + config["arrayjob"]["id"]
        self.array_params: str = config["arrayjob"]["header"].rstrip("\n")
        self.sync_options: str = config["options"]["sync"]

    def header(self) -> str:
        return self.header

    def body(self) -> str:
        return self.body

    def resource(self, mem: str = None, slot: str = None) -> str:
        if mem is None:
            mem = self.default_mem
        if slot is None:
            slot = self.default_slot
        return self.resource_params.replace("{mem}", mem).replace("{slot}", slot)

    def array_header_with_cmd(self, command: str) -> tuple:
        length = bash_array_len(command)
        array_header = self.array_params.replace("{start}", "1").replace("{end}", str(length)).replace("{step}", "1")
        array = f'array=($({command}))'
        # like following
        # elem=${array[$(($SEG_TASK_ID-1))]}
        elem = "elem=${array[$((" + self.array_job_id + "-1))]}"
        return array_header, "\n".join([array, elem])

    def array_with_ls(self, ls_pattern: str):
        ls_command = " ".join(["ls", ls_pattern])
        return self.array_header_with_cmd(ls_command)

    def sync_qsub_command(self) -> list:
        return ["qsub"] + self.sync_options

def read_config(path: str = "~/.config/qsubpy_config.toml") -> Config:
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
#$ -l s_veme={mem} -l mem_req={mem}
#$ -pe def_slot {slot}
"""

[arrayjob]
id = "SEG_TASK_ID"
header = "#$ -t {start}-{end}:{step}"

[options]
sync = ["-sync", "y"]
'''

def generate_defulat_config():
    import os
    path = os.environ.get("QSUBPY_CONFIG")
    if path is None:
        path = "~/.config/qsubpy_config.toml"
    
    if os.path.exists(path):
        return

    if not os.path.exists("~/.config"):
        os.makedirs("~/.config")

    with open(path, "w") as f:
        f.write(SHIROKANE_CONFIG)