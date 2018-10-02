# -*- coding: utf-8 -*-
import csv
from collections import defaultdict

import os
import sys

from gos_asm.algo import default_configuration
from gos_asm.algo.data_structures.assemblies import AssemblyPoint

from bg.breakpoint_graph import BreakpointGraph
from bg.grimm import GRIMMReader
from bg.genome import BGGenome
from bg.distances import single_cut_and_join_distance
from bg.utils import recursive_dict_update
from networkx import Graph
import importlib


class EvaluationExperiment(object):
    def __init__(self, config_file_path, evaluation_dir_path):
        self.config_file_path = config_file_path
        self.evaluation_dir_path = evaluation_dir_path


class AssemblyPointEvaluation(object):
    def __init__(self, ap):
        self.ap = ap
        self.HC = False
        self.GOC = False


def get_fragment_name_and_sign(fragment):
    if fragment.startswith("-"):
        fragment_name, fragment_sign = fragment[1:], fragment[0]
    else:
        fragment_name, fragment_sign = fragment, "+"
    return fragment_name, fragment_sign


def get_pair_of_fragments_vertices(fragment1, fragment2):
    fragment1_name, fragment1_sign = get_fragment_name_and_sign(fragment=fragment1)
    fragment2_name, fragment2_sign = get_fragment_name_and_sign(fragment=fragment2)
    fragment_1_suffix = "h" if fragment1_sign == "+" else "t"
    fragment_2_suffix = "t" if fragment1_sign == "+" else "h"
    return fragment1_name + fragment_1_suffix, fragment2_name + fragment_2_suffix


def get_closure_fragments(fragments, cnt, chr_type):
    if chr_type == "$":
        return fragments[cnt + 1:]
    elif chr_type == "@":
        return fragments[cnt + 1:] + fragments[:cnt]
    else:
        return []


def get_html_document_header():
    return """
        <html>
        <head>
            <link rel='stylesheet' href='http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css'>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
            <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
            <style>
            .table {
                max-width: 100%;
            }
            </style>
        </head>
        <body>
        <div class="container">
    """


def get_html_document_footer():
    return """
        </div>
        </body>
        </html>

    """


def add_collapse_header(heading, suffix, result, parent_data=None):
    result.append("<div class='panel-group' id='collapse_{suffix}_parent_group' {data_parent}>".format(data_parent="" if parent_data is None else "data-parent='#{pd}'".format(pd=parent_data),
                                                                                                       suffix=suffix))
    result.append("<div class='panel panel-default'>")
    result.append("<div class='panel-heading'>")
    result.append("<h4 class='panel-title'>")
    result.append("<a data-toggle='collapse' data-parent='#collapse_{suffix}_parent_group' href='#collapse_{suffix}'>{heading}</a>".format(suffix=suffix, heading=heading))
    result.append("</h4>")
    result.append("</div>")
    result.append("<div id='collapse_{suffix}' class='panel-collapse collapse'>".format(suffix=suffix))
    result.append("<div class='panel-body'>")


def add_collapse_footer(result):
    result.append("</div>")
    result.append("</div>")
    result.append("</div>")
    result.append("</div>")


def get_html_report_experiment_entry(experiment):
    try:
        module_path, file_name = os.path.split(experiment.config_file_path)
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        module_name = file_name[:file_name.rfind(".")]
        if module_name in sys.modules:
            del sys.modules[module_name]
        module = importlib.import_module(module_name)
        config = module.configuration
    except Exception:
        raise
    config = recursive_dict_update(default_configuration.configuration, config)

    result = []
    result.append("<hr>")
    result.append("<hr>")
    result.append("<h1>{experiment_name}</h1>".format(experiment_name=config.get("experiment_name", "Experiment XXX")))

    reference_chr_fragments_order_full_path = os.path.join(experiment.evaluation_dir_path, "chr_fragments_order.txt")
    assembled_chains_full_path = os.path.join(config["gos-asm"]["output"]["dir"], config["gos-asm"]["output"]["chains_file"])
    assembly_points_file_full_path = os.path.join(config["gos-asm"]["output"]["dir"], config["gos-asm"]["output"]["assembly_points_file"])

    assembly_point_evaluation = []
    with open(assembly_points_file_full_path, newline="") as csv_file:
        reader = csv.reader(csv_file, delimiter="|")
        headers = next(reader)
        headers = [header.strip() for header in headers]
        for row in reader:
            entry = {key: value for key, value in zip(headers, row)}
            ap = AssemblyPoint.from_assembly_points_file(separated_values=entry)
            assembly_point_evaluation.append(AssemblyPointEvaluation(ap=ap))

    genomes_ref_chr_fragments_orders = defaultdict(list)
    current_genome = None
    with open(reference_chr_fragments_order_full_path, "rt") as source:
        for line in source:
            if len(line.strip()) == 0 or line.strip().startswith("#"):
                continue
            elif line.strip().startswith(">"):
                current_genome = BGGenome(line.strip()[1:])
                genomes_ref_chr_fragments_orders[current_genome].append(line.strip())
            elif current_genome is not None:
                genomes_ref_chr_fragments_orders[current_genome].append(line.strip())

    assembled_genome_fragments_orders = defaultdict(list)
    current_genome = None
    with open(assembled_chains_full_path, "rt") as source:
        for line in source:
            if len(line.strip()) == 0 or line.strip().startswith("#"):
                continue
            elif line.strip().startswith(">"):
                current_genome = BGGenome(line.strip()[1:])
                assembled_genome_fragments_orders[current_genome].append(line.strip())
            elif current_genome is not None:
                assembled_genome_fragments_orders[current_genome].append(line.strip())

    bg = BreakpointGraph()
    for file_path in [reference_chr_fragments_order_full_path, assembled_chains_full_path]:
        with open(file_path, "rt") as source:
            bg.update(GRIMMReader.get_breakpoint_graph(source, merge_edges=False))

    scjs = {}
    genomes_fragmentation_total = {}
    target_genomes = [BGGenome(genome_name) for genome_name in config["gos-asm"]["input"]["target_organisms"]]

    for genome in target_genomes:
        assembled_chains = assembled_genome_fragments_orders[genome]
        reference_chains = genomes_ref_chr_fragments_orders[genome]
        source = assembled_chains + reference_chains
        bg = GRIMMReader.get_breakpoint_graph(source, merge_edges=False)
        scjs[genome] = single_cut_and_join_distance(bg)

    reference_assembly_graph = {}
    current_genome = None
    with open(reference_chr_fragments_order_full_path, "rt") as source:
        for line in source:
            if len(line.strip()) == 0 or line.strip().startswith("#"):
                continue
            elif line.strip().startswith(">"):
                current_genome = BGGenome(line.strip()[1:])
                if current_genome not in reference_assembly_graph:
                    reference_assembly_graph[current_genome] = Graph()
                    genomes_fragmentation_total[current_genome] = 0
            elif current_genome is not None:
                fragments = line.strip().split()
                *fragments, chr_type = fragments
                genomes_fragmentation_total[current_genome] += len(fragments) - 1
                for fragment1, fragment2 in zip(fragments[:-1], fragments[1:]):
                    v1, v2 = get_pair_of_fragments_vertices(fragment1, fragment2)
                    reference_assembly_graph[current_genome].add_edge(v1, v2, attr_dict={"type": "HC"})
                if chr_type == "@":
                    v1, v2 = get_pair_of_fragments_vertices(fragments[-1], fragments[0])
                    reference_assembly_graph[current_genome].add_edge(v1, v2, attr_dict={"type": "HC"})
                for cnt, fragment in enumerate(fragments):
                    closure_fragments = get_closure_fragments(fragments, cnt, chr_type)
                    for fr in closure_fragments:
                        v1, v2 = get_pair_of_fragments_vertices(fragment, fr)
                        if not reference_assembly_graph[current_genome].has_edge(v1, v2):
                            reference_assembly_graph[current_genome].add_edge(v1, v2, attr_dict={"type": "GOC"})


    for ap_eval in assembly_point_evaluation:
        fragment1 = ap_eval.ap.fragment1
        fragment2 = ap_eval.ap.fragment2
        fragment1_sign = ap_eval.ap.fragment1_sign
        fragment2_sign = ap_eval.ap.fragment2_sign
        fr1_suffix = "h" if fragment1_sign == "+" else "t"
        fr2_suffix = "t" if fragment2_sign == "+" else "h"
        v1, v2 = fragment1 + fr1_suffix, fragment2 + fr2_suffix
        graph = reference_assembly_graph[ap_eval.ap.info.target_color.colors.pop()]
        if graph.has_edge(v1, v2):
            type_ = graph[v1][v2]["type"]
            if type_ == "HC":
                ap_eval.HC = True
                ap_eval.GOC = True
            elif type_ == "GOC":
                ap_eval.GOC = True

    exp_id = config.get("experiment_name", "Experiment XXX")
    exp_id = "_".join(exp_id.split())

    result.append("<h2>Experiment info</h2>")
    result.append("<div class='well'>")
    result.append("<p>" + config.get("experiment_info", "No info").replace("\n", "<br>") + "</p>")
    result.append("</div>")

    result.append("<h3>Evaluation</h3>")
    result.append("<h4>Per target genome</h4>")
    for genome in target_genomes:
        g_suffix = exp_id + "_" + genome.name
        genome_ap = [ap_eval for ap_eval in assembly_point_evaluation if ap_eval.ap.info.target_color.colors.pop().name == genome.name]
        add_collapse_header(heading=genome.name, suffix=g_suffix, result=result)
        result.append("<div class='container' style='width:100%;'>")

        add_collapse_header(heading="Assembly points", suffix=g_suffix + "_assembly_point", result=result, parent_data="collapse_{suffix}".format(suffix=g_suffix))
        add_ap_table(genome_ap, result)
        add_collapse_footer(result=result)
        result.append("</div>")
        result.append("<p>SCJ distance between produced assembly and a reference one: <b>{scj_distance}</b></p>".format(scj_distance=scjs[genome]))

        result.append("<ul>")
        total_cnt = len(genome_ap)
        result.append("<li><p>Total # of identified assembly points: <b>{ap_cnt}</b></p></li>".format(ap_cnt=total_cnt))
        hc_cnt = len([ap for ap in genome_ap if ap.HC])

        result.append("<li><p>Correct assembly points: <b>{HC_cnt}</b></p></li>".format(HC_cnt=hc_cnt))
        goc_cnt = len([ap for ap in genome_ap if ap.GOC and not ap.HC])

        result.append(
                "<li><p>Correct from Global Gene Order (GOC) perspective assembly points: <b>{GOC_cnt}</b></p></li>".format(GOC_cnt=goc_cnt))
        incorrect_cnt = len([ap for ap in genome_ap if not ap.HC and not ap.GOC])
        result.append("<li><p>Incorrect assembly points: <b>{ic_cnt}</b></p></li>".format(ic_cnt=incorrect_cnt))

        result.append("</ul>")

        # result.append("</div>")

        result.append("<h5>Relative portions of identified assembly points</h5>")
        result.append("<div class='progress'>")

        for value, style in zip([hc_cnt, goc_cnt, incorrect_cnt],  ["success", "info", "danger"]):
            value_prs = value * 100 / total_cnt
            result.append(
                    '<div class="progress-bar progress-bar-{style}" role="progressbar" aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100" style="width: {value}%">'
                    ''.format(style=style, value=value_prs))
            result.append("<span>{value:.2f}%</span>".format(value=value_prs, style=style))
            result.append("</div>")
        result.append("</div>")

        overall_cnt = genomes_fragmentation_total[genome]

        result.append("<h5>Absolute portions of identified assembly points</h5>")
        result.append("<div class='progress'>")

        for value, style in zip([hc_cnt, goc_cnt, incorrect_cnt],  ["success", "info", "danger"]):
            value_prs = value * 100 / overall_cnt
            result.append(
                    '<div class="progress-bar progress-bar-{style}" role="progressbar" aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100" style="width: {value}%">'
                    ''.format(style=style, value=value_prs))
            result.append("<span>{value:.2f}%</span>".format(value=value_prs, style=style))
            result.append("</div>")
        add_collapse_footer(result=result)

    result.append("<h4>Overall results</h4>")

    add_collapse_header(heading="Assembly_points", suffix=exp_id, result=result)
    add_ap_table(assembly_point_evaluation, result)
    add_collapse_footer(result=result)

    # result.append("<div class='row'>")
    result.append("<ul>")
    total_cnt = len(assembly_point_evaluation)
    result.append("<li><p>Total # of identified assembly points: <b>{ap_cnt}</b></p></li>".format(ap_cnt=total_cnt))
    hc_cnt = len([ap for ap in assembly_point_evaluation if ap.HC])

    result.append("<li><p>Correct assembly points: <b>{HC_cnt}</b></p></li>".format(HC_cnt=hc_cnt))
    goc_cnt = len([ap for ap in assembly_point_evaluation if ap.GOC and not ap.HC])

    result.append(
            "<li><p>Correct from Global Gene Order (GOC) perspective assembly points: <b>{GOC_cnt}</b></p></li>".format(GOC_cnt=goc_cnt))
    incorrect_cnt = len([ap for ap in assembly_point_evaluation if not ap.HC and not ap.GOC])
    result.append("<li><p>Incorrect assembly points: <b>{ic_cnt}</b></p></li>".format(ic_cnt=incorrect_cnt))

    result.append("</ul>")

    result.append("<h5>Relative portions of identified assembly points</h5>")
    result.append("<div class='progress'>")

    for value, style in zip([hc_cnt, goc_cnt, incorrect_cnt],  ["success", "info", "danger"]):
        value_prs = value * 100 / total_cnt
        result.append(
                '<div class="progress-bar progress-bar-{style}" role="progressbar" aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100" style="width: {value}%">'
                ''.format(style=style, value=value_prs))
        result.append("<span>{value:.2f}%</span>".format(value=value_prs, style=style))
        result.append("</div>")
    result.append("</div>")

    overall_cnt = sum([value for key, value in genomes_fragmentation_total.items() if key in target_genomes])
    result.append("<h5>Absolute portions of identified assembly points</h5>")
    result.append("<div class='progress'>")

    for value, style in zip([hc_cnt, goc_cnt, incorrect_cnt],  ["success", "info", "danger"]):
        value_prs = value * 100 / overall_cnt
        result.append(
                '<div class="progress-bar progress-bar-{style}" role="progressbar" aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100" style="width: {value}%">'
                ''.format(style=style, value=value_prs))
        result.append("<span>{value:.2f}%</span>".format(value=value_prs, style=style))
        result.append("</div>")
    result.append("</div>")
    return "\n".join(result)


def add_ap_table(assembly_point_evaluation, result):
    result.append("<table class=\"table table-bordered\">")
    result.append("<thead>")
    result.append("<tr>")
    header_string = "<th>id</th><th>HC</th><th>GOC</th><th>G</th><th>v1 - v2</th>" \
                    "<th>f1 - f2</th><th>S</th><th>R1 - R2</th>" \
                    "<th>R guidance</th><th>MC</th>"
    result.append(header_string)
    result.append("</tr>")
    result.append("</thead>")
    result.append("<tbody>")
    for ap_eval in assembly_point_evaluation:
        add_ap_eval_html_entry(ap_eval, result)
    result.append("</tbody>")
    result.append("</table>")


def get_condensed_repeat_guidance(repeat_guidance):
    return [repeat[:-3] for repeat in repeat_guidance[::2]]


def add_ap_eval_html_entry(ap_eval, result):
    if ap_eval.HC:
        tr_class = "success"
    elif ap_eval.GOC:
        tr_class = "info"
    else:
        tr_class = "danger"
    result.append("<tr class='{tr_class}'>".format(tr_class=tr_class))
    entry_string = "<td>{id}</td><td>{HC}</td><td>{GOC}</td><td>{genome}</td><td>{vertex1:>7} - {vertex2:<7}</td>" \
                   "<td>{fragment1} - {fragment2}</td><td>{sedge}</td><td>{repeat1} - {repeat2}</td><td>{r_guidance}</td>" \
                   "<td>{MC}</td>"
    ok_entry = "<span class=\"glyphicon glyphicon-ok\"></span>"
    result.append(entry_string.format(id=ap_eval.ap.id, HC=ok_entry if ap_eval.HC else "", GOC=ok_entry if ap_eval.GOC else "",
                                      genome=ap_eval.ap.info.target_color.colors.pop().name[:2],
                                      vertex1=ap_eval.ap.vertex1, vertex2=ap_eval.ap.vertex2,
                                      fragment1=ap_eval.ap.fragment1_sign + ap_eval.ap.fragment1,
                                      fragment2=ap_eval.ap.fragment2_sign + ap_eval.ap.fragment2,
                                      repeat1=ap_eval.ap.info.repeat_info["repeat_name_1"] + "(" + ap_eval.ap.info.repeat_info[
                                          "repeat_dir_1"] + ")",
                                      repeat2=ap_eval.ap.info.repeat_info["repeat_name_2"] + "(" + ap_eval.ap.info.repeat_info[
                                          "repeat_dir_2"] + ")",
                                      r_guidance=", ".join(get_condensed_repeat_guidance(ap_eval.ap.info.repeat_info["repeat_guidance"])),
                                      MC=", ".join(sorted(color.name[:2] for color in ap_eval.ap.info.target_multicolor.colors)),
                                      sedge=str(ap_eval.ap.info.support_edge)
                                      ))
    result.append("</tr>")


def get_overall_html_report(experiments):
    entries = [get_html_document_header()]
    for experiment in experiments:
        entries.append(get_html_report_experiment_entry(experiment=experiment))
    entries.append(get_html_document_footer())
    return "".join(entries)
