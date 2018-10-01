# -*- coding: utf-8 -*-
import os

exp_dir = os.path.dirname(__file__)
mgra_path = os.environ.get('MGRA_PATH', None)
if mgra_path is None:
    mgra_path = "indel_mgra"

configuration = {
    "experiment_name": "Chimp 2000",
    "experiment_info": """
        6 genomes are taken as input: Chimpanzee, Mouse, Rat, Dog, Opossum.
        Chimpanzee genome is fragment with repeats of length >= 2000 bp
        All duplicated genes are filtered out.
        (((chimpanzee,(mouse, rat)),(cat,dog)),opossum); is utilized for observed genome set.
    """,
    "gos-asm": {
        "input": {
            "block_orders_file_paths": [
                os.path.join(exp_dir, "blocks.txt")
            ],
            "phylogenetic_tree": "(((chimpanzee,(mouse, rat)),(cat,dog)),opossum);",
            "target_organisms": ["chimpanzee"],
            "repeats_bridges_file": os.path.join(exp_dir, "bridges.txt")
        },
        "output": {
            "dir": os.path.join(exp_dir, "output")
        }
    },
    "mgra": {
            "executable_path": mgra_path,
        },
    "algorithm": {
        "executable_containers": [
        ],
        "pipeline": {
            "entries_names": ["task_input",                         # reading data
                              "tmc_wrapper_CCA_balanced",           #   ###
                              "cyclic_wrapper_MGRA_CCA_balanced",   #   Assembly points detection
                              "tmc_wrapper_phylo",                  #   ###
                              "task_output"]                        # outputting data
        }
    }
}
