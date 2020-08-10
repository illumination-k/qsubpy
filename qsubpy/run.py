import os
import subprocess

from qsubpy import utils


def command_mode(cmd, mem, slot, name, ls):
    utils.make_sh_file(cmd, mem, slot, name, ls)
    
    subprocess.run(["qsub", name])
    os.remove(name)

def file_mode(path, mem, slot, name, ls):
    cmd = utils.read_sh(path)
    utils.make_sh_file(path, mem, slot, name, ls)

    subprocess.run(["qsub", name])
    os.remove(name)