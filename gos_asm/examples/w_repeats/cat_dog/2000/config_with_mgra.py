# -*- coding: utf-8 -*-
import os
from teamcity import is_running_under_teamcity

exp_dir = os.path.dirname(__file__)
if is_running_under_teamcity():
    mgra_path = "/usr/local/bin/indel_mgra"
else:
    mgra_path = "/Users/aganezov/mgra-gos-asm/build/src/mgra/indel_mgra"

configuration = {
    "experiment_name": "Cat Dog 2000 with MGRA",
    "experiment_info": """
        6 genomes are taken as input: Chimpanzee, Mouse, Rat, Cat, Dog, Opossum.
        Cat genome is fragment with repeats of length >= 2000 bp
        Dog genome is fragment with repeats of length >= 2000 bp
        All duplicated genes are filtered out.
        ((((chimpanzee, human),(mouse, rat)),(cat,dog)),opossum); is utilized for observed genome set.
        MGRA is utilized to obtain guidance breakpoint graph.
    """,
    "mgra": {
        "executable_path": mgra_path
    },
    "gos-asm": {
        "input": {
            "block_orders_file_paths": [
                os.path.join(exp_dir, "blocks.txt")
            ],
            "phylogenetic_tree": "((((chimpanzee, human),(mouse, rat)),(cat,dog)),opossum);",
            "target_organisms": ["cat", "dog"],
            "repeats_bridges_file": os.path.join(exp_dir, "bridges.txt")
        },
        "output": {
            "dir": os.path.join(exp_dir, "output_mgra")
        }
    },
    "algorithm": {
        "executable_containers": [
            # {
            #     "reference": "ec"
            # }
        ],
        # "ec": [
        #     {
        #         "name": "ec_assembling",
        #         "entries_names": [
        #             "task_CCA",
        #             "task_GG_MGRA",
        #         ]
        #     },
        # ],

        "pipeline": {
            "entries_names": ["task_input", "tmc_wrapper", "task_GG_MGRA", "tmc_wrapper_MGRA", "task_output"]
        }
    }
}
