# -*- coding: utf-8 -*-
import os

exp_dir = os.path.dirname(__file__)

configuration = {
    "experiment_name": "Chimp 400 no repeats",
    "experiment_info": """
        6 genomes are taken as input: Chimpanzee, Mouse, Rat, Dog, Cat and Opossum.
        Chimpanzee genome is fragment with repeats of length >= 400 bp.
        No flanking repeats are present in the input data.
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
            # "repeats_bridges_file": os.path.join(exp_dir, "bridges.txt")
        },
        "output": {
            "dir": os.path.join(exp_dir, "output")
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
            "entries_names": ["task_input", "stage1", "task_output"],
            "self_loop": True
        }
    }
}
