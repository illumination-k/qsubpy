from .config import Config

class Template:
    def __init__(self, config: Config):
        self.header = []
        self.body = []
        self.config = config

    def make_templates(self, array_command: str=None, mem: str=None, slot: str=None, common_variables=None) -> str:
        self.header.append(self.config.header)
        self.header.append(self.config.resource(mem, slot))
        
        if array_command is not None:
            array_header, array_body = self.config.array_header_with_cmd(array_command)
            self.header.append(array_header)
            self.body.append(array_body)
        self.body.append(self.config.body)

        if common_variables is not None:
            self.body.append(make_common_variables_params(common_variables))
        
        return self.header + self.body

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


def make_array_params(files):
    if files is None:
        return []

    files_num = len(files)
    array_param = f'#$ -t 1-{files_num}:1'

    # make below
    # file_list=(file1 file2 file3)
    # file=${file_list[$(($SGE_TASK_ID-1))]}
    file_list = "file_list=(" + " ".join(files) + ")" 
    file = "file=${file_list[$(($SGE_TASK_ID-1))]}"
    return [array_param, file_list, file]


def make_common_variables_params(common_variables):
    if common_variables is None:
        return []

    ret = []
    for k, v in common_variables.items():
        ret.append(k + "=" + str(v))
    return ret


def make_params(mem, slot, files=None, common_variables=None):
    mem_param = f'#$ -l s_vmem={mem} -l mem_req={mem}'
    slot_param = f'#$ -pe def_slot {slot}'
    ret = [mem_param, slot_param]

    ret += make_array_params(files)
    ret += make_common_variables_params(common_variables)
    ret.append("\n")

    return ret


def make_templates(mem, slot, files=None, common_variables=None):
    params = make_params(mem, slot, files, common_variables)
    script = HEADER + params + BODY

    return script

#TODO! implement chunk mode... below is example
"""
#!/bin/bash

arrays=(
    "1 2 3"
    "11 22 33"
    "111 222 333"
)

for array in "${arrays[@]}"; do
    echo "------------"
    data=(${array[@]})
    for a in ${data[@]}; do
        echo ${a}
    done
done
"""