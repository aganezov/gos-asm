# -*- coding: utf-8 -*-
import logging

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
            "entries_names": ["stage1"],
            "self_loop": True
        }
    }
}
