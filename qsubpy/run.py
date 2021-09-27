import os
import yaml
import subprocess
import argparse

from qsubpy.utils import make_sh_file, read_sh
from qsubpy.qsub import Qsub

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


class Settings:
    import yaml

    def __init__(self, path: str, dry_run: bool):
        with open(path, "r") as f:
            settings = yaml.safe_load(f)
        self.stages = settings.get("stages")
        if self.stages is None:
            raise ValueError("Stages need")
        self.job_name = settings.get("job_name")
        self.defalut_mem = settings.get("default_mem")
        self.default_slot = settings.get("default_slot")
        self.common_varialbes = settings.get("common_variables", [])
        self.remove = settings.get("remove")
        self.mode = settings.get("mode", "ord")
        self.test = settings.get("test") is not None

        if self.mode not in ["sync", "ord", "dry_run"]:
            raise ValueError(f"invalid mode {self.mode}, plz use sync, ord or dry_run")

        self.dry_run = dry_run
        if not self.dry_run:
            self.dry_run = settings.get("dry_run") or self.mode.lower() == "dry_run"

    def start_log(self):
        logger.debug("start qsubpy with setting mode")
        logger.info(f"start {self.job_name} with mode {self.mode}\n")
        logger.info(f"-------------")
        logger.info(f"default memory: {self.defalut_mem}")
        logger.info(f"default slots: {self.default_slot}")
        logger.debug(common_varialbes)
        if self.dry_run:
            logger.critical(f"dry_run is True, only generated sh files...")


class Stage:
    def __init__(self, stage: dict, settings: Settings):
        self.settings = settings
        self.name = stage.get("name")
        self.mem = stage.get("mem", settings.defalut_mem)
        self.slot = stage.get("slot", settings.default_slot)
        self.ls_patten = stage.get("ls")
        self.array_cmd = stage.get("array_cmd")

        # set command
        self.cmd = stage.get("cmd")
        if self.cmd is None:
            path = stage.get("file")
            if path is None:
                raise RuntimeError("cmd or file is required in each stage!")
            self.cmd = read_sh(path)
        else:
            self.cmd = [self.cmd]

    def debug(self):
        logger.debug(f"mem: {self.mem}, slot: {self.slot}")
        logger.debug(f"ls_pattern: {self.ls_patten}")
        logger.debug(f"array_cmd: {self.array_cmd}")
        logger.debug(f'cmd: {" ".join(self.cmd)}')

    def run_stage(self, hold_jid: str = None) -> str:
        logger.info(f"start stage: {self.name}")
        self.debug()
        name = make_sh_file(
            cmd=self.cmd,
            mem=self.mem,
            slot=self.slot,
            name=self.name,
            array_command=self.array_cmd,
            ls_pattern=self.ls_patten,
            chunks=None,
            common_variables=self.settings.common_varialbes,
        )

        if self.settings.dry_run and not self.settings.test:
            logger.debug("dry_run and test is false")
            return None

        next_jid = None
        qsub = Qsub(test=self.settings.test)
        if self.settings.mode == "sync":
            qsub.sync(name)
        elif self.settings.mode == "ord":
            next_jid = qsub.ord(name, hold_jid)

        logger.info(f"end {self.name}...")
        return next_jid


def setting_mode(path, dry_run):
    import time

    time_dict = {}
    start_time = time.time()

    settings = Settings(path, dry_run)

    hold_jid = None
    for _stage in settings.stages:
        stage_start = time.time()

        # get params
        stage = Stage(_stage, settings)

        # update hold jid if mode is ord
        hold_jid = stage.run_stage(hold_jid)

        stage_end = time.time()
        key = stage.name + "_proceeded_time"
        time_dict[key] = stage_end - stage_start
        if settings.mode == "sync":
            logger.info(f"proceeded time is {time_dict[key]}")

    end_time = time.time()
    if settings.mode == "sync":
        time_dict["job_proceeded_time"] = end_time - start_time
        with open("time.log", "w") as f:
            for k, v in time_dict.items():
                f.write(k + ":" + str(v) + "\n")
