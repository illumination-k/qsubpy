HEADER = [
    "#!/bin/bash",
    "#$ -S /bin/bash",
    "#$ -cwd",
]

BODY = [
    "source ~/.bashrc",
    "source ~/.bash_profile",
    "set -eu"
]


def make_params(mem, slot):
    mem_param = f'#$ -l s_vmem={mem} -l mem_req={mem}'
    slot_param = f'#$ -pe def_slot {slot}'
    return [mem_param, slot_param]


def make_default_templates(mem, slot, **kwarg):
    params = make_params(mem, slot)
    script = HEADER + params + BODY

    return script


def make_array_templates(mem, slot, files):
    params = make_params(mem, slot)
    files_num = len(files)
    array_param = f'#$ -t 1-{files_num}:1'

    # make below
    # file_list=(file1 file2 file3)
    # file=${file_list[$(($SGE_TASK_ID-1))]}
    file_list = "file_list=(" + " ".join(files) + ")" 
    file = "file=${file_list[$(($SGE_TASK_ID-1))]}"

    script = HEADER + params + [array_param, file_list, file] + BODY
    return script
