# -*- coding: utf-8 -*-
import os
from teamcity import is_running_under_teamcity

exp_dir = os.path.dirname(__file__)

if is_running_under_teamcity():
    mgra_path = "/usr/local/bin/indel_mgra"
else:
    mgra_path = "/Users/aganezov/mgra-gos-asm/build/src/mgra/indel_mgra"

configuration = {
    "experiment_name": "Chimp 400 with MGRA (no repeats)",
    "experiment_info": """
        6 genomes are taken as input: Chimpanzee, Mouse, Rat, Dog, Cat, Opossum.
        Chimpanzee genome is fragment with repeats of length >= 400 bp
        All duplicated genes are filtered out.
        (((chimpanzee,(mouse, rat)),(cat,dog)),opossum); is utilized for observed genome set.
        MGRA is utilized after usual stages
    """,
    "mgra": {
        "executable_path": mgra_path,
    },
    "gos-asm": {
        "input": {
            "block_orders_file_paths": [
                os.path.join(exp_dir, "blocks.txt")
            ],
            "phylogenetic_tree": "(((chimpanzee,(mouse, rat)),(cat,dog)),opossum);",
            "target_organisms": ["chimpanzee"],
            # "repeats_bridges_file": os.path.join(exp_dir, "bridges.txt")
        },
        "output": {
            "dir": os.path.join(exp_dir, "output_mgra")
        }
    },
    "algorithm": {
        "executable_containers": [
            {
                "reference": "stages"
            }
        ],
        "stages": [
            {
                "name": "stage1",
                "entries_names": [
                    "task_CCA"
                ]
            }
        ],

        "pipeline": {
            "entries_names": ["task_input", "tmc_wrapper", "task_GG_MGRA", "tmc_wrapper_MGRA", "task_output"]
        }
    }
}
