# -*- coding: utf-8 -*-

#########################################################################################################
#
#
#
#
#
#
#
#########################################################################################################
import argparse
import csv
import sys

import importlib
import os
from algo import default_configuration
from algo.data_structures.assemblies import AssemblyPoint
from bg import BreakpointGraph, GRIMMReader, BGGenome
from bg.distances import single_cut_and_join_distance
from bg.utils import recursive_dict_update
from evaluation.gos_asm_html import AssemblyPointEvaluation, get_pair_of_fragments_vertices, get_closure_fragments
from networkx import Graph

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gene order based scaffolder evaluation on artificially fragmented genomes")
    parser.add_argument("configuration_file",
                        nargs=1,
                        help="A fully qualifying path to gos-asm configuration .py file." +
                             "File must contain a configuration entry which is described with dictionary python structure")
    parser.add_argument("evaluation_dir", nargs=1)
    arguments = parser.parse_args()
    manager = None
    config = {}
    evaluation_dir = ""
    try:
        module_path, file_name = os.path.split(arguments.configuration_file[0])
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        module_name = file_name[:file_name.rfind(".")]
        module = importlib.import_module(module_name)
        config = module.configuration
    except Exception as exc:
        print("Error importing configurations")
        exit(1)
    config = recursive_dict_update(default_configuration.configuration, config)
    evaluation_dir = arguments.evaluation_dir[0]

    reference_chr_fragments_order_full_path = os.path.join(evaluation_dir, "chr_fragments_order.txt")
    assembled_filtered_chains_order_full_path = os.path.join(config["gos-asm"]["output"]["dir"],
                                                             config["gos-asm"]["output"]["filtered_chains_file"])
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

    bg = BreakpointGraph()
    for file_path in [reference_chr_fragments_order_full_path, assembled_chains_full_path]:
        with open(file_path, "rt") as source:
            bg.update(GRIMMReader.get_breakpoint_graph(source, merge_edges=False))

    SCJ = single_cut_and_join_distance(breakpoint_graph=bg)

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
            elif current_genome is not None:
                fragments = line.strip().split()
                *fragments, chr_type = fragments
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

    print("SCJ distance:", SCJ)
    print("HC:", len([ap_eval for ap_eval in assembly_point_evaluation if ap_eval.HC]))
    print("GOC:", len([ap_eval for ap_eval in assembly_point_evaluation if ap_eval.GOC]))
    print("Incorrect:", len([ap_eval for ap_eval in assembly_point_evaluation if not ap_eval.GOC and not ap_eval.HC]))
    print("Total:", len(assembly_point_evaluation))




