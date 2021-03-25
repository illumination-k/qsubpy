# Utility for qsub of UGE

## Installation

`pip install --user git+https://github.com/illumination-k/qsubpy`

If not work, please try below..., 

```
git clone https://github.com/illumination-k/qsubpy.git
cd qsubpy
pip install -e .
```

## Usage

default mem: 4G
default slot: 1

### Basic qsubpy

```bash
qsubpy -c 'echo hello' --mem 4G --slot 1
```

The below file is generated and run qsub

```bash
#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -l s_vmem=4G -l mem_req=4G
#$ -pe def_slot 1
source ~/.bashrc
source ~/.bash_profile
set -eu
echo hello
```

### qsubpy ls (array job)

easy to use `for f in $(ls); do qsub script.sh $f; done;` with array job.
Using in `qsubpy/qsubpy` directory

```bash
qsubpy -c 'echo $elem' --ls "*.py"
```

You can use eleme variable in the command. The below file is generated and run qsub

```bash
#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -l s_vmem=4G -l mem_req=4G
#$ -pe def_slot 1
#$ -t 1-8:1
array=($(ls *.py))
elem=${array[$(($SGE_TASK_ID-1))]}

source ~/.bashrc
source ~/.bash_profile
set -eu
echo $elem
```

### Build Workflow with settings.yml

```bash
nohup qsubpy -s settings.yml &
```

### Dry Run

if you use `--dry_run` flag, qsubpy generates sh files only.

```bash
qsubpy -c 'echo hello' --dry_run
```