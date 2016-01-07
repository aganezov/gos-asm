# -*- coding: utf-8 -*-
from gos_asm.algo.data_structures.assemblies import AssemblyPointInfo
from bg import Multicolor
from gos_asm.algo.data_structures.evolutionary_scenarios import EvolutionaryScenario
from gos_asm.algo.shared.bg import has_edge_between_two_vertices, get_irregular_vertex, get_repeat_info, get_full_support_edge, \
    get_regular_vertex, get_full_irregular_multicolor
from copy import deepcopy

non_conflicting_evolutionary_scenarios = [
    ("000",
     {"iedge1": EvolutionaryScenario.didnt_exist, "iedge2": EvolutionaryScenario.didnt_exist, "sedge": EvolutionaryScenario.didnt_exist}),
    (
        "100",
        {"iedge1": EvolutionaryScenario.existed, "iedge2": EvolutionaryScenario.didnt_exist, "sedge": EvolutionaryScenario.didnt_exist}),
    (
        "010",
        {"iedge1": EvolutionaryScenario.didnt_exist, "iedge2": EvolutionaryScenario.existed, "sedge": EvolutionaryScenario.didnt_exist}),
    ("110", {"iedge1": EvolutionaryScenario.existed, "iedge2": EvolutionaryScenario.existed, "sedge": EvolutionaryScenario.didnt_exist}),
    ("001", {"iedge1": EvolutionaryScenario.didnt_exist, "iedge2": EvolutionaryScenario.didnt_exist, "sedge": EvolutionaryScenario.existed})
]


def get_assembly_point_info(graph, vertex1, vertex2, data, guidance_graph=None):
    vertex1 = get_regular_vertex(iedge1)
    vertex2 = get_regular_vertex(iedge2)

    if guidance_graph is None:
        guidance_graph = graph
    if guidance_graph.has_edge(vertex1=vertex1, vertex2=vertex2):
        support_edge = guidance_graph.get_condensed_edge(vertex1, vertex2)
    else:
        support_edge = None

    repeat1_name, repeat1_dir = get_repeat_info(iedge1)
    repeat2_name, repeat2_dir = get_repeat_info(iedge2)
    repeat_info = {
        "repeat_name_1": repeat1_name,
        "repeat_name_2": repeat2_name,
        "repeat_dir_1": repeat1_dir,
        "repeat_dir_2": repeat2_dir
    }
    evolutionary_scenarios = {}
    for e_scenario_name, e_scenario in non_conflicting_evolutionary_scenarios:
        evolutionary_scenarios[e_scenario_name] = get_assembly_score(iedge1=iedge1, iedge2=iedge2, evolutionary_scenario=e_scenario,
                                                                     data=data)
    return AssemblyPointInfo(iedge1=iedge1, iedge2=iedge2,
                             support_edge=support_edge,
                             evolutionary_scenarios=evolutionary_scenarios,
                             repeat_info=repeat_info,
                             target_multicolor=data["gos-asm"]["target_multicolor"])


def get_full_multicolor(data):
    bg = data["gos-asm"]["bg"]
    return Multicolor(*bg.get_overall_set_of_colors())


def compute_evolutionary_score(multicolor, scenario, data):
    tree = data["gos-asm"]["phylogenetic_tree"]
    if scenario == EvolutionaryScenario.existed:
        color_to_split = multicolor
    else:
        if "full_multicolor" not in data["gos-asm"]["cache"]:
            data["gos-asm"]["cache"]["full_multicolor"] = get_full_multicolor(data=data)
        full_multicolor = data["gos-asm"]["cache"]["full_multicolor"]
        color_to_split = full_multicolor - multicolor
    return len(Multicolor.split_colors(multicolor=color_to_split, guidance=tree.consistent_multicolors,
                                       account_for_color_multiplicity_in_guidance=False))


def get_assembly_score(full_ie1_multicolor, full_ie2_multicolor, sedge_multicolor, target_multicolor, evolutionary_scenario, data):
    target_multicolor = deepcopy(target_multicolor)

    iedge_1_score_before = compute_evolutionary_score(multicolor=deepcopy(full_ie1_multicolor), scenario=evolutionary_scenario,
                                                      data=data)
    iedge_2_score_before = compute_evolutionary_score(multicolor=deepcopy(full_ie2_multicolor), scenario=evolutionary_scenario,
                                                      data=data)
    sedge_score_before = compute_evolutionary_score(multicolor=deepcopy(sedge_multicolor), scenario=evolutionary_scenario,
                                                    data=data)

    iedge_1_color_after = full_ie1_multicolor - target_multicolor
    iedge_1_score_after = compute_evolutionary_score(multicolor=iedge_1_color_after, scenario=evolutionary_scenario,
                                                     data=data)
    iedge_2_color_after = full_ie2_multicolor - target_multicolor
    iedge_2_score_after = compute_evolutionary_score(multicolor=iedge_2_color_after, scenario=evolutionary_scenario,
                                                     data=data)
    sedge_color_after = sedge_multicolor + target_multicolor
    sedge_score_after = compute_evolutionary_score(multicolor=sedge_color_after, scenario=evolutionary_scenario,
                                                   data=data)

    return {
        "before": {
            "iedge1": {
                "color": full_ie1_multicolor,
                "score": iedge_1_score_before
            },
            "iedge2": {
                "color": full_ie2_multicolor,
                "score": iedge_2_score_before
            },
            "s_edge": {
                "color": sedge_multicolor,
                "score": sedge_score_before
            }
        },
        "after": {
            "iedge1": {
                "color": iedge_1_color_after,
                "score": iedge_1_score_after
            },
            "iedge2": {
                "color": iedge_2_color_after,
                "score": iedge_2_score_after
            },
            "sedge": {
                "color": sedge_color_after,
                "score": sedge_score_after
            }
        }
    }
