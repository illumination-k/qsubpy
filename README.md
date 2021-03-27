# Utility for qsub of UGE

## Installation

`pip install --user git+https://github.com/illumination-k/qsubpy`

If not work, please try below..., 

```
git clone https://github.com/illumination-k/qsubpy.git
cd qsubpy
pip install -e .
```
## Config

Can be configured to fit your environment.
You can set header and body of scripts, how to set resource and array job, qsub options and how to get job id. If you use qsubpy first, qsubpy generate the config file in `${HOME}/.config/qsubpy_config.toml`. Default settings is [config.toml](https://github.com/illumination-k/qsubpy/blob/master/config.toml) 

qsubpy generate following files

```
scripts.header
resource.header
arrayjob.header(optional)

scripts.body

[your cmd]
```

## Usage

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

source ~/.bashrc
source ~/.bash_profile
set -eu

array=($(ls *.py))
elem=${array[$(($SGE_TASK_ID-1))]}
echo $elem
```

### Array Job

```bash
qsubpy -c "echo $elem" --array_cmd "cat test/barcodes.tsv"
```

```bash
#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -l s_veme=4G -l mem_req=4G
#$ -pe def_slot 1
#$ -t 1-10:1

source ~/.bashrc
source ~/.bash_profile
set -eu
array=($(cat test/barcodes.tsv))
elem=${array[$(($SEG_TASK_ID-1))]}
echo $elem
```


### Build Workflow with settings.yml

#### Mode

You can choose mode from ord, sync or dry_run. If you choose dry_run mode, qsubpy generates sh files only.

##### ord

qsubpy automatically get job id and run qsub with options such as `-hold-jid xxxxx` according to the order of settigns.yml.

```bash
qsubpy -s settings.yml
```

qsubpy get jid by regex in config from qsub stdout.

##### sync

qsubpy run qsub with otpions such as `-sync -y`. Qsubpy run the stage and wait finishing job and run next stage.

```bash
nohup qsubpy -s settings.yml &
```

### Dry Run

if you use `--dry_run` flag, qsubpy generates sh files only.

```bash
qsubpy -c 'echo hello' --dry_run
```

