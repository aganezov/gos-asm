# -*- coding: utf-8 -*-
import logging
import os

exp_dir = os.path.dirname(__file__)
mgra_path = os.environ.get('MGRA_PATH', None)
if mgra_path is None:
    mgra_path = "indel_mgra"

configuration = {
    "gos-asm": {
        "input": {
            "block_orders_file_paths": [],
            "phylogenetic_tree": "",
            "target_organisms": [],
            "repeats_bridges_file": ""
        },
        "output": {
            "debug_log_enabled": True,
            "debug_log_file": "debug.log",
            "console_log_enabled": True,
            "console_log_level": logging.DEBUG,
            "assembly_points_file": "assembly_points.txt",
            "output_chains": True,
            "chains_file": "chains.txt",
            "output_filtered_chains": True,
            "filtered_chains_file": "filtered_chains.txt"
        },
    },
    "mgra": {
        "executable_path": mgra_path,
    },
    "algorithm": {
        "tasks": {
            "paths": []
        },
        "executable_containers": [
            # {
            #     "reference": "stages"
            # },
        ],
        # "stages": [
        #     {
        #         "name": "stage1",
        #         "entries_names": ["task_input", "task_CCA"]
        #     }
        # ],

        "pipeline": {
            "entries_names": ["task_input",  # reading data
                              "tmc_wrapper_CCA_balanced",  # ###
                              "cyclic_wrapper_MGRA_CCA_balanced",  # Assembly points detection
                              "tmc_wrapper_phylo",  # ###
                              "task_output"]  # outputting data
        }
    }
}
