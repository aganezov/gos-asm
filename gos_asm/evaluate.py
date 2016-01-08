# -*- coding: utf-8 -*-
import sys
import os
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, ".."))

from gos_asm.evaluation.gos_asm_html import EvaluationExperiment, get_overall_html_report

chimp400wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "400", "config.py")
chimp400wrMGRA = os.path.join(current_dir, "examples", "w_repeats", "chimp", "400", "config_with_mgra.py")
chimp800wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "800", "config.py")
chimp1200wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "1200", "config.py")
chimp1600wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "1600", "config.py")
chimp2000wr = os.path.join(current_dir, "examples", "w_repeats", "chimp", "2000", "config.py")

chimp400nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "400", "config.py")
chimp800nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "800", "config.py")
chimp1200nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "1200", "config.py")
chimp1600nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "1600", "config.py")
chimp2000nr = os.path.join(current_dir, "examples", "n_repeats", "chimp", "2000", "config.py")

catDog2000wr = os.path.join(current_dir, "examples", "w_repeats", "cat_dog", "2000", "config.py")
catDog2000wrMGRA = os.path.join(current_dir, "examples", "w_repeats", "cat_dog", "2000", "config_with_mgra.py")

all_fragmented_Chimp400wr = os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "config.py")
all_fragmented_Chimp400wrMGRA = os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "config_with_mgra.py")

configs_for_experiments_to_run = [
    chimp400wr,
    chimp400wrMGRA,
    # chimp800wr,
    # chimp1200wr,
    # chimp1600wr,
    # chimp2000wr,
    # chimp400nr,
    # chimp800nr,
    # chimp1200nr,
    # chimp1600nr,
    # chimp2000nr,
    catDog2000wr,
    catDog2000wrMGRA,
    all_fragmented_Chimp400wr,
    all_fragmented_Chimp400wrMGRA
]

experiments_to_evaluate = [
    # EvaluationExperiment(config_file_path=chimp400wr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "chimp", "400", "evaluation")),
    EvaluationExperiment(config_file_path=chimp400wrMGRA,
                         evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "chimp", "400", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp800wr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "chimp", "800", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp1200wr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "chimp", "1200", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp1600wr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "chimp", "1600", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp2000wr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "chimp", "2000", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp400nr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "n_repeats", "chimp", "400", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp800nr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "n_repeats", "chimp", "800", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp1200nr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "n_repeats", "chimp", "1200", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp1600nr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "n_repeats", "chimp", "1600", "evaluation")),
    # EvaluationExperiment(config_file_path=chimp2000nr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "n_repeats", "chimp", "2000", "evaluation")),
    # EvaluationExperiment(config_file_path=catDog2000wr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "cat_dog", "2000", "evaluation")),
    # EvaluationExperiment(config_file_path=catDog2000wrMGRA,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "cat_dog", "2000", "evaluation")),
    # EvaluationExperiment(config_file_path=all_fragmented_Chimp400wr,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "evaluation")),
    # EvaluationExperiment(config_file_path=all_fragmented_Chimp400wrMGRA,
    #                      evaluation_dir_path=os.path.join(current_dir, "examples", "w_repeats", "allChimp", "400", "evaluation")),
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
