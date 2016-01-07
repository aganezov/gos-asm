# -*- coding: utf-8 -*-

from gos_asm.evaluation.gos_asm_html import EvaluationExperiment, get_overall_html_report

chimp400 = "/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/400/config.py"
chimp800 = "/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/800/config.py"
chimp1200 = "/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/1200/config.py"
chimp1600 = "/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/1600/config.py"
chimp2000 = "/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/2000/config.py"

configs_for_experiments_to_run = [
    chimp400, chimp800, chimp1200, chimp1600, chimp2000
]

experiments_to_evaluate = [
    EvaluationExperiment(config_file_path=chimp400,
                         evaluation_dir_path="/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/400/evaluation"),
    EvaluationExperiment(config_file_path=chimp800,
                         evaluation_dir_path="/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/800/evaluation"),
    EvaluationExperiment(config_file_path=chimp1200,
                         evaluation_dir_path="/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/1200/evaluation"),
    EvaluationExperiment(config_file_path=chimp1600,
                         evaluation_dir_path="/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/1600/evaluation"),
    EvaluationExperiment(config_file_path=chimp2000,
                         evaluation_dir_path="/Users/aganezov/Programming/gos-asm/gos_asm/examples/w_repeats/chimp/2000/evaluation"),

]

if __name__ == "__main__":
    for config_path in configs_for_experiments_to_run:
        os.system("{python_path} {gos_asm_path} {config_path}".format(
                python_path=sys.executable,
                gos_asm_path=os.path.join(os.path.dirname(__file__), "../gos-asm.py"),
                config_path=config_path
        ))
    html_report_text = get_overall_html_report(experiments_to_evaluate)
    with open("report.html", "wt") as destination:
        print(html_report_text, file=destination)
