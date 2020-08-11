import os
import subprocess

from qsubpy import utils

import logging
logger = logging.getLogger(__name__)

def command_mode(cmd, mem, slot, name, ls, dry_run):
    name = utils.make_sh_file([cmd+"\n"], mem, slot, name, ls)

    if not dry_run:
        subprocess.run(["qsub", name])
    # os.remove(name)

def file_mode(path, mem, slot, name, ls, dry_run):
    cmd = utils.read_sh(path)
    name = utils.make_sh_file(cmd, mem, slot, name, ls)

    if not dry_run:
        subprocess.run(["qsub", name])
    # os.remove(name)


def setting_mode(path):
    import yaml
    import time
    from qsubpy.sync_qsub import sync_qsub

    time_dict = {}
    start_time = time.time()

    with open(path, 'r') as f:
        settings = yaml.safe_load(f)
    
    defalut_mem = settings.get("default_mem")
    default_slot = settings.get("default_slot")
    common_varialbes = settings.get("common_variables")

    remove = settings.get("remove")
    dry_run = settings.get("dry_run")

    for stage in settings['stages']:
        logger.info(f'start {stage}')
        stage_start = time.time()
        # get params
        name = stage.get('name')
        mem = stage.get('mem', defalut_mem)
        slot = stage.get('slot', default_slot)
        ls_patten = stage.get('ls')
        
        # get cmd and run qsub by sync mode to keep in order
        cmd = stage.get('cmd')

        if cmd is not None:
            name = utils.make_sh_file([cmd], mem, slot, name, ls_patten, common_varialbes)
            
            if dry_run is None:
                sync_qsub(name)
        else:
            path = stage.get('file')
            if path is None:
                raise RuntimeError("cmd or file is required in each stage!")
            cmd = utils.read_sh(path)
            name = utils.make_sh_file(cmd, mem, slot, name, ls_patten, common_varialbes)
            
            if dry_run is None:
                sync_qsub(name)

        if remove and (dry_run is None or not dry_run):
            os.remove(name)

        stage_end = time.time()
        key = name + "_proceeded_time"
        time_dict[key] = stage_end - stage_start
        logger.info(f'end {stage}... proceeded time is {time_dict[key]}')

    end_time = time.time()
    time_dict["job_proceeded_time"] = end_time - start_time
    with open("time.log", 'w') as f:
        for k, v in time_dict.items():
            f.write(k + ":" + str(v) + "\n")
