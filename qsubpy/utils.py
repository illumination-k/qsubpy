import os
import re

import logging
logger = logging.getLogger(__name__)

def wildcard2re(pattern):
    """
    convert unix wildcard to python regix
    Args:
        pattern (str): unix wildcard
    Returns:
        str: string for python regix
    """
    pattern = pattern.replace(".", "\.")
    pattern = pattern.replace("?", ".")
    pattern = pattern.replace("*", ".*")
    pattern = pattern.replace("[!", '[^')
    # TODO! {,} -> {|}
    pattern = "^" + pattern + "$"
    return pattern


def ls(arg=None, ls_pattern=None):
    """
    mimic unix ls commands
    Args:
        arg (None): not implemented
        ls_pattern (string): path and wildcard eg., /path/to/*.py
    Retruns:
        list: files list in ls_pattern
    """
    dir_path, pattern = os.path.split(ls_pattern)
    if dir_path == '':
        dir_path = os.getcwd()
    files = os.listdir(dir_path)

    if arg == "-d":
        files = [ f for f in files if os.path.isdir(f) ]

    if pattern is not None:
        # convert wild card to re
        pattern = wildcard2re(pattern)
        prog = re.compile(pattern)
        files = [ f for f in files if prog.search(f) is not None ]

    return files


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



def make_sh_file(cmd, mem, slot, name, ls_pattern, chunks=None, common_variables=None):
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
    from .templates import Template
    from .config import read_config, generate_defulat_config
    generate_defulat_config()
    config = read_config()
    
    template = Template(config)

    if ls_pattern is not None:
        files = ls(ls_pattern=ls_pattern)
    else:
        files=None    
        
    script = template.make_templates(array_command=None, mem=mem, slot=slot, common_variables=common_variables)

    script += cmd

    if name is None:
        name = make_uuid()
    if not name.endswith(".sh"):
        name += ".sh"

    with open(name, "w") as f:
        f.write("\n".join(script))
    
    return name