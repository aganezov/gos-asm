# -*- coding: utf-8 -*-
from copy import deepcopy

from bg.multicolor import Multicolor

from gos_asm.algo.data_structures.evolutionary_scenarios import EvolutionaryScenario

non_conflicting_evolutionary_scenarios = [
    ("000",
     {"iedge1": EvolutionaryScenario.didnt_exist, "iedge2": EvolutionaryScenario.didnt_exist, "sedge": EvolutionaryScenario.didnt_exist}),
    (
        "100",
        {"iedge1": EvolutionaryScenario.existed, "iedge2": EvolutionaryScenario.didnt_exist, "sedge": EvolutionaryScenario.didnt_exist}),
    (
        "001",
        {"iedge1": EvolutionaryScenario.didnt_exist, "iedge2": EvolutionaryScenario.existed, "sedge": EvolutionaryScenario.didnt_exist}),
    ("101", {"iedge1": EvolutionaryScenario.existed, "iedge2": EvolutionaryScenario.existed, "sedge": EvolutionaryScenario.didnt_exist}),
    ("010", {"iedge1": EvolutionaryScenario.didnt_exist, "iedge2": EvolutionaryScenario.didnt_exist, "sedge": EvolutionaryScenario.existed})
]


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
    return len(Multicolor.split_colors(multicolor=color_to_split, guidance=tree.vtree_consistent_multicolors,
                                       account_for_color_multiplicity_in_guidance=False))


def get_assembly_score(full_ie1_multicolor, full_ie2_multicolor, sedge_multicolor, target_multicolor, evolutionary_scenario, data):
    target_multicolor = deepcopy(target_multicolor)

    iedge_1_score_before = compute_evolutionary_score(multicolor=deepcopy(full_ie1_multicolor), scenario=evolutionary_scenario["iedge1"],
                                                      data=data)
    iedge_2_score_before = compute_evolutionary_score(multicolor=deepcopy(full_ie2_multicolor), scenario=evolutionary_scenario["iedge2"],
                                                      data=data)
    sedge_score_before = compute_evolutionary_score(multicolor=deepcopy(sedge_multicolor), scenario=evolutionary_scenario["sedge"],
                                                    data=data)

    iedge_1_color_after = full_ie1_multicolor - target_multicolor
    iedge_1_score_after = compute_evolutionary_score(multicolor=iedge_1_color_after, scenario=evolutionary_scenario["iedge1"],
                                                     data=data)
    iedge_2_color_after = full_ie2_multicolor - target_multicolor
    iedge_2_score_after = compute_evolutionary_score(multicolor=iedge_2_color_after, scenario=evolutionary_scenario["iedge2"],
                                                     data=data)
    sedge_color_after = sedge_multicolor + target_multicolor
    sedge_score_after = compute_evolutionary_score(multicolor=sedge_color_after, scenario=evolutionary_scenario["sedge"],
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
            "sedge": {
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
