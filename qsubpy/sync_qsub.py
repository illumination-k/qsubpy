import subprocess


def sync_qsub(sh_file):
    cmd = ["qsub", "-sync", "y", sh_file]
    p = subprocess.Popen(cmd)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError(f'{" ".join(cmd)} exit code {p.returncode}')
