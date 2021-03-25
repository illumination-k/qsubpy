import os
import subprocess
import argparse

from utils import make_sh_file, read_sh

import logging

logger = logging.getLogger(__name__)


def command_mode(args: argparse.Namespace):
    cmd = args.command
    mem = args.mem
    slot = args.slot
    name = args.name
    ls = args.ls
    array_command = args.array_cmd
    dry_run = args.dry_run
    name = make_sh_file(
        cmd=[cmd + "\n"],
        mem=mem,
        slot=slot,
        name=name,
        array_command=array_command,
        ls_pattern=ls,
    )

    if not dry_run:
        subprocess.run(["qsub", name])
    # os.remove(name)


def file_mode(path, mem, slot, name, ls, dry_run):
    cmd = read_sh(path)
    name = make_sh_file(cmd=cmd, mem=mem, slot=slot, name=name, ls_pattern=ls)

    if not dry_run:
        subprocess.run(["qsub", name])
    # os.remove(name)


def setting_mode(path, dry_run):
    import yaml
    import time
    from sync_qsub import sync_qsub

    time_dict = {}
    start_time = time.time()

    with open(path, "r") as f:
        settings = yaml.safe_load(f)

    job_name = settings.get("job_name")
    defalut_mem = settings.get("default_mem")
    default_slot = settings.get("default_slot")
    common_varialbes = settings.get("common_variables")
    remove = settings.get("remove")

    logger.debug("start qsubpy with setting mode")
    logger.info(f"start {job_name}\n")
    logger.info(f"-------------")
    logger.info(f"default memory: {defalut_mem}")
    logger.info(f"default slots: {default_slot}")

    if not dry_run:
        dry_run = settings.get("dry_run")

    if dry_run:
        logger.critical(f"dry_run is True, only generated sh files...")

    if remove and (dry_run is None or not dry_run):
        logger.info(
            f"remove is True, when job is finished with exit code 0, remove log files and sh file"
        )

    for stage in settings["stages"]:
        stage_start = time.time()
        # get params
        name = stage.get("name")
        mem = stage.get("mem", defalut_mem)
        slot = stage.get("slot", default_slot)
        ls_patten = stage.get("ls")
        array_cmd = stage.get("array_cmd")
        logger.info(f"start stage: {name}")
        # get cmd and run qsub by sync mode to keep in order
        cmd = stage.get("cmd")

        if cmd is not None:
            name = make_sh_file(
                cmd=[cmd],
                mem=mem,
                slot=slot,
                name=name,
                array_command=array_cmd,
                ls_pattern=ls_patten,
                chunks=None,
                common_variables=common_varialbes,
            )

            if dry_run is None or not dry_run:
                sync_qsub(name)
        else:
            path = stage.get("file")
            if path is None:
                raise RuntimeError("cmd or file is required in each stage!")
            cmd = read_sh(path)
            name = make_sh_file(
                cmd=cmd,
                mem=mem,
                slot=slot,
                name=name,
                ls_pattern=ls_patten,
                array_command=array_cmd,
                chunks=None,
                common_variables=common_varialbes,
            )

            if dry_run is None or not dry_run:
                sync_qsub(name)

        if remove and (dry_run is None or not dry_run):
            os.remove(name)

        stage_end = time.time()
        key = name + "_proceeded_time"
        time_dict[key] = stage_end - stage_start
        logger.info(f"end {stage}...")
        logger.info(f"proceeded time is {time_dict[key]}")

    end_time = time.time()
    time_dict["job_proceeded_time"] = end_time - start_time
    with open("time.log", "w") as f:
        for k, v in time_dict.items():
            f.write(k + ":" + str(v) + "\n")
