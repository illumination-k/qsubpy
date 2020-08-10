import os
import re


def wildcard2re(pattern):
    pattern = pattern.replace(".", "\.")
    pattern = pattern.replace("?", ".")
    pattern = pattern.replace("*", ".*")
    pattern = pattern.replace("[!", '[^')
    # TODO! {,} -> {|}
    return pattern


def ls(arg=None, pattern=None):
    files = os.listdir(".")
    if pattern is not None:
        # convert wild card to re
        pattern = wildcard2re(pattern)
        prog = re.compile(pattern)
    if arg == "-d":
        files = [ f for f in files if os.path.isdir(f) ]

    files = [ f for f in files if prog.search(f) is not None ]
    return files


def make_uuid():
    import uuid
    return str(uuid.uuid4())


def read_sh(path):
    lines = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            lines.append(line.rstrip("\n"))
    return lines


def make_sh_file(cmd, mem, name, ls):
    from qsubpy import templates

    if ls is None:
        script = templates.make_default_templates(mem, slot)
    else:
        files = ls(ls)
        script = templates.make_array_templates(mem, slot, files)

    script += cmd

    if name is None:
        name = make_uuid() + ".sh"

    with open(name, "w") as f:
        f.write("\n".join(script))