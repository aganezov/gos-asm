# -*- coding: utf-8 -*-
import logging
import os

from gos.manager import Manager


class AssemblyManager(Manager):
    def __init__(self, config):

        super(AssemblyManager, self).__init__(config=config)
        self.logger = logging.getLogger("GOS-ASM")
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(self.configuration["gos-asm"]["output"]["console_log_level"])
        formatter = logging.Formatter('%(asctime)s - %(name)7s - %(levelname)-7s - %(message)s',
                                      datefmt="%m-%d %H:%M:%S")
        ch.setFormatter(formatter)

        output_dir = self.configuration["gos-asm"]["output"]["dir"]
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        log_file_name = self.configuration["gos-asm"]["output"]["debug_log_file"]
        log_file_full_path = os.path.join(output_dir, log_file_name)
        fh = logging.FileHandler(log_file_full_path, mode="wt")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        if self.configuration["gos-asm"]["output"]["console_log_enabled"]:
            self.logger.addHandler(ch)
        if self.configuration["gos-asm"]["output"]["debug_log_enabled"]:
            self.logger.addHandler(fh)

        self.logger.debug("Initiating tasks")
        self.initiate_tasks()
        self.logger.debug("Instantiating tasks")
        self.instantiate_tasks()
        self.logger.debug("Initiating executable containers")
        self.initiate_executable_containers()
        self.logger.debug("Instantiating executable containers")
        self.instantiate_executable_containers()
        self.data = {
            "gos-asm": {
                "cache": {

                },
                "assembly_points": []
            }
        }
        self.logger.info("Targeted for assembly organisms: {organisms}"
                         "".format(organisms=str(self.configuration["gos-asm"]["input"]["target_organisms"])))

    def initiate_tasks(self):
        current_file_name = os.path.dirname(__file__)
        gos_asm_predefined_tasks = [
            os.path.join(current_file_name, "algo", "tasks", "asm"),
            os.path.join(current_file_name, "algo", "tasks", "io"),
            os.path.join(current_file_name, "algo", "tasks", "mgra")]
        gos_asm_predefined_ec = [
            os.path.join(current_file_name, "algo", "executable_containers", "wrappers.py"),
        ]
        paths_list = self.configuration["algorithm"]["tasks"]["paths"]
        for gos_asm_predefined_task in gos_asm_predefined_tasks:
            if gos_asm_predefined_task not in paths_list:
                paths_list.append(gos_asm_predefined_task)
        self.configuration["algorithm"]["executable_containers"].append({"paths": gos_asm_predefined_ec})
        super(AssemblyManager, self).initiate_tasks()
