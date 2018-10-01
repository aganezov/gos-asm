# -*- coding: utf-8 -*-
import os
import sys

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, ".."))

from gos_asm.evaluation.gos_asm_html import EvaluationExperiment, get_overall_html_report


################################################################################################
#
#
#
#
#
################################################################################################


opossum400nr = os.path.join(current_dir, "examples", "n_repeats", "opossum", "400", "config.py")
opossum400wr = os.path.join(current_dir, "examples", "w_repeats", "opossum", "400", "config.py")
opossum2000nr = os.path.join(current_dir, "examples", "n_repeats", "opossum", "2000", "config.py")
opossum2000wr = os.path.join(current_dir, "examples", "w_repeats", "opossum", "2000", "config.py")


mr400nr = os.path.join(current_dir, "examples", "n_repeats", "mouse_rat", "400", "config.py")
mr400wr = os.path.join(current_dir, "examples", "w_repeats", "mouse_rat", "400", "config.py")
mr2000nr = os.path.join(current_dir, "examples", "n_repeats", "mouse_rat", "2000", "config.py")
mr2000wr = os.path.join(current_dir, "examples", "w_repeats", "mouse_rat", "2000", "config.py")


dog400nr = os.path.join(current_dir, "examples", "n_repeats", "dog", "400", "config.py")
dog400wr = os.path.join(current_dir, "examples", "w_repeats", "dog", "400", "config.py")
dog400wr_balanced = os.path.join(current_dir, "examples", "w_repeats", "dog", "400", "config_b.py")
dog2000nr = os.path.join(current_dir, "examples", "n_repeats", "dog", "2000", "config.py")
dog2000wr = os.path.join(current_dir, "examples", "w_repeats", "dog", "2000", "config.py")
dog2000wr_balanced = os.path.join(current_dir, "examples", "w_repeats", "dog", "2000", "config_b.py")
dog2000wrPhylo = os.path.join(current_dir, "examples", "w_repeats", "dog", "2000", "config_phylo.py")

dog2000wr_unique = os.path.join(current_dir, "examples", "old_vs_new", "unique", "repeats", "dog", "2000", "config.py")
dog400wr_unique = os.path.join(current_dir, "examples", "old_vs_new", "unique", "repeats", "dog", "400", "config.py")




########################################################################################################################
#
#
#
#
#
########################################################################################################################



funestus7 = os.path.join(current_dir, "examples", "n_repeats", "anopheles", "funestus_7", "config.py")
funestus4 = os.path.join(current_dir, "examples", "n_repeats", "anopheles", "funestus_4", "config.py")



########################################################################################################################


chimp400wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "400", "config.py")
chimp400wrMGRA = os.path.join(current_dir, "examples", "w_repeats", "chimp", "400", "config_with_mgra.py")
allChimp400wr_balanced = os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "config_b.py")
chimp400wrMGRAPhylo = os.path.join(current_dir, "examples", "w_repeats", "chimp", "400", "config_phylo.py")


chimp800wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "800", "config.py")
chimp1200wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "1200", "config.py")
chimp1600wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "1600", "config.py")
chimp2000wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "2000", "config.py")

chimp400nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "400", "config.py")
chimp400nrMGRA = os.path.join(current_dir, "examples", "n_repeats", "chimp", "400", "config_with_mgra.py")
chimp800nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "800", "config.py")
chimp1200nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "1200", "config.py")
chimp1600nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "1600", "config.py")
chimp2000nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "2000", "config.py")

catDog2000wr = os.path.join(current_dir, "examples", "w_repeats", "cat_dog", "2000", "config.py")
catDog2000wrMGRA = os.path.join(current_dir, "examples", "w_repeats", "cat_dog", "2000", "config_with_mgra.py")

all_fragmented_Chimp400wr = os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "config.py")
all_fragmented_Chimp400wrMGRA = os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "config_with_mgra.py")

allFChimp400wrMGRA = os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "config_with_mgra.py")
allFChimp400wrMGRAPhylo = os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "config_phylo.py")
allChimp400wr_unique_balanced = os.path.join(current_dir, "examples", "old_vs_new", "unique", "repeats", "allChimp", "400", "config_b.py")
allChimp400wr = os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "config_b.py")

configs_for_experiments_to_run = [
    allChimp400wr,
    # allChimp400wr_balanced,
    # allChimp400wr_unique_balanced,
    # chimp400wrMGRAPhylo
    # allFChimp400wrMGRA,
    # allFChimp400wrMGRAPhylo,
    # opossum400nr,
    # opossum400wr,
    # opossum2000nr,
    # opossum2000wr,
    # mr400nr,
    # mr400wr,
    # mr2000nr,
    # mr2000wr,
    # dog400nr,
    # dog400wr,
    # dog400wr_balanced,
    # dog2000wr_balanced,
    # dog400wr_unique,
    # dog2000nr,
    # dog2000wr,
    # dog2000wrPhylo,
    # dog2000wr_unique
    # funestus7,
    # funestus4
]

experiments_to_evaluate = [

    EvaluationExperiment(config_file_path=allChimp400wr,
                         evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "evaluation")),
    # EvaluationExperiment(config_file_path=allChimp400wr_unique_balanced,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "evaluation")),
    # EvaluationExperiment(config_file_path=dog400wr_balanced,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "dog", "400", "evaluation")),
    # EvaluationExperiment(config_file_path=dog2000wr_balanced,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "dog", "2000", "evaluation")),

]

if __name__ == "__main__":

    for config_path in configs_for_experiments_to_run:
        # print(config_path)
        os.system("{python_path} {gos_asm_path} {config_path}".format(
                python_path=sys.executable,
                gos_asm_path=os.path.join(os.path.dirname(__file__), "gos-asm.py"),
                config_path=config_path
        ))
    html_report_text = get_overall_html_report(experiments_to_evaluate)
    with open(os.path.join(current_dir, "evaluation", "report.html"), "wt") as destination:
        print(html_report_text, file=destination)
