import subprocess
from qsubpy.config import read_config

import logging

logger = logging.Logger(__name__)

CONFIG = read_config()

class Qsub:
    def __init__(self, test: bool = False):
        self.config = read_config()
        self.test = test

    def sync(self, sh_file):
        cmd = self.config.sync_qsub_command()
        cmd += [sh_file]
        if self.test:
            logging.info(" ".join(cmd))
            return
        else:
            logging.debug(" ".join(cmd))
            
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode != 0:
            raise RuntimeError(f'{" ".join(cmd)} exit code {p.returncode}')

    def ord(self, sh_file, hold_jid: str = None):
        if hold_jid is None:
            cmd = ["qsub", sh_file]
        else:
            cmd = self.config.ord_qsub_command(hold_jid) + [sh_file]
        if self.test:
            logging.info(" ".join(cmd))
            return
        else:
            logging.debug(" ".join(cmd))

        next_jid = qsub_with_jid(cmd)
        return next_jid


def get_jid(out: str) -> str:
    """get jid from output
    """
    import re
    r = CONFIG.jid_re
    jid = re.search(r, out).group("jid")
    return jid

def qsub_with_jid(cmd: list, std: str="stdout") -> str:
    """run qsub and get jid
    """

    p = subprocess.run(" ".join(cmd), shell=True, capture_output=True, executable="/bin/bash")
    if std == "stdout":
        out = p.stdout
    elif std == "stderr":
        out = p.stderr
    else:
        raise ValueError("stdout or stderr in std")

    out = out.decode("utf-8")
    jid = get_jid(out)
    return jid



