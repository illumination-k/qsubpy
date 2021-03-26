import subprocess
from qsubpy.config import read_config

CONFIG = read_config()

def sync_qsub(sh_file):
    cmd = CONFIG.sync_options()
    cmd += [sh_file]
    p = subprocess.Popen(cmd)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError(f'{" ".join(cmd)} exit code {p.returncode}')
