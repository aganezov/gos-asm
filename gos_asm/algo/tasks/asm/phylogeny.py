# -*- coding: utf-8 -*-
import itertools

import networkx as nx
from bg.multicolor import Multicolor
from gos.tasks import BaseTask
from networkx import Graph

from gos_asm.algo.data_structures.assemblies import AssemblyPoint, AssemblyPointInfo
from gos_asm.algo.shared.assembly_point import non_conflicting_evolutionary_scenarios, get_assembly_score
from gos_asm.algo.shared.gos_asm_bg import get_full_irregular_multicolor, get_repeat_info, create_k_break_from_assembly_point
from gos_asm.algo.shared.gos_asm_logging import log_bg_stats
from gos_asm.algo.tasks.asm.shared import suitable_for_assembly_fragment_ends_vertex, get_irregular_edge_by_vertex_color, assembly_is_allowed, \
    get_repeat_entry, get_repeat_guidance

phylo_threshold = 1


def has_support_edge(graph, v1, v2):
    return graph.has_edge(vertex1=v1, vertex2=v2)


def get_maximal_phylogenetic_score(evolutionary_scenarios):
    result = 0
    result_scenario = None
    for scenario, entry in evolutionary_scenarios.items():
        before = 0
        before += entry["before"]["iedge1"]["score"]
        before += entry["before"]["iedge2"]["score"]
        before += entry["before"]["sedge"]["score"]
        after = 0
        after += entry["after"]["iedge1"]["score"]
        after += entry["after"]["iedge2"]["score"]
        after += entry["after"]["sedge"]["score"]
        if before - after > result:
            result = before - after
            result_scenario = scenario
    return result_scenario, result


def get_minimal_phylogenetic_score(evolutionary_scenarios):
    result = 100
    result_scenario = None
    for scenario, entry in evolutionary_scenarios.items():
        before = 0
        before += entry["before"]["iedge1"]["score"]
        before += entry["before"]["iedge2"]["score"]
        before += entry["before"]["sedge"]["score"]
        after = 0
        after += entry["after"]["iedge1"]["score"]
        after += entry["after"]["iedge2"]["score"]
        after += entry["after"]["sedge"]["score"]
        if before - after < result:
            result = before - after
            result_scenario = scenario
    return result_scenario, result


class PhylogenyBasedAssemblyTask(BaseTask):
    name = 'task_PhyloA'

    def run(self, manager):
        manager.logger.info("=" * 80)
        manager.logger.info("Assembling with Phylogeny Assembly strategy")
        bg = manager.data["gos-asm"]["bg"]

        log_bg_stats(bg=bg, logger=manager.logger)
        target_multicolor = manager.data["gos-asm"]["target_multicolor"]
        assembly_cnt = 0
        ap_header_printed = False

        kbreaks = []
        max_cc_size = 0
        for cc_cnt, cc in enumerate(bg.connected_components_subgraphs(copy=False)):
            if len(list(cc.nodes())) > max_cc_size:
                max_cc_size = len(list(cc.nodes()))
            possible_assemblies_graph = Graph()
            for vertex in (v for v in cc.nodes() if v.is_regular_vertex):
                if suitable_for_assembly_fragment_ends_vertex(graph=bg, reg_vertex=vertex, target_multicolor=target_multicolor):
                    possible_assemblies_graph.add_node(vertex)
            if len(possible_assemblies_graph.nodes()) > 1:
                manager.logger.debug("suitable vertices {}".format(len(possible_assemblies_graph.nodes())))
            # if len(list(possible_assemblies_graph.nodes())) > 1000:
            #     print("passing large cc")

            for v1, v2 in itertools.combinations(list(possible_assemblies_graph.nodes()), 2):
                if assembly_is_allowed(graph=bg, vertex1=v1, vertex2=v2, target_multicolor=target_multicolor, data=manager.data) \
                        and has_support_edge(graph=bg, v1=v1, v2=v2):
                    s_edge = bg.get_condensed_edge(vertex1=v1, vertex2=v2)
                    evolutionary_scenarios = {}
                    full_ie1_multicolor = get_full_irregular_multicolor(vertex=v1, data=manager.data, graph=bg)
                    full_ie2_multicolor = get_full_irregular_multicolor(vertex=v2, data=manager.data, graph=bg)
                    for e_scenario_name, e_scenario in non_conflicting_evolutionary_scenarios:
                        evolutionary_scenarios[e_scenario_name] = get_assembly_score(full_ie1_multicolor=full_ie1_multicolor,
                                                                                     full_ie2_multicolor=full_ie2_multicolor,
                                                                                     sedge_multicolor=s_edge.multicolor,
                                                                                     target_multicolor=target_multicolor,
                                                                                     evolutionary_scenario=e_scenario, data=manager.data)

                    scenario, maximal_score = get_maximal_phylogenetic_score(evolutionary_scenarios)
                    scenario, minimal_score = get_minimal_phylogenetic_score(evolutionary_scenarios)
                    if minimal_score > phylo_threshold:
                        possible_assemblies_graph.add_edge(v1, v2, attr_dict={"weight": maximal_score})
                    elif minimal_score == 1:
                        iedge1 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v1, color=target_multicolor.colors.pop())
                        iedge2 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v2, color=target_multicolor.colors.pop())
                        s_edge = bg.get_condensed_edge(vertex1=v1, vertex2=v2)
                        r1_name, r1_dir = get_repeat_info(iedge1)
                        r2_name, r2_dir = get_repeat_info(iedge2)
                        r1_entry = get_repeat_entry(repeat_name=r1_name, repeat_direction=r1_dir)
                        r2_entry = get_repeat_entry(repeat_name=r2_name, repeat_direction=r2_dir)
                        repeat_info = {
                            "repeat_name_1": r1_name,
                            "repeat_name_2": r2_name,
                            "repeat_dir_1": r1_dir,
                            "repeat_dir_2": r2_dir
                        }
                        try:
                            repeat_guidance = get_repeat_guidance(genome=target_multicolor.colors.pop(), repeat1_entry=r1_entry,
                                                                  repeat2_entry=r2_entry,
                                                                  data=manager.data)
                        except nx.networkx.exception.NetworkXNoPath:
                            raise Exception("Pair of edges must suitable for assembly with repeats guidance")
                        repeat_info["repeat_guidance"] = repeat_guidance
                        evolutionary_scenarios = {}
                        full_ie1_multicolor = get_full_irregular_multicolor(vertex=v1, data=manager.data, graph=bg)
                        full_ie2_multicolor = get_full_irregular_multicolor(vertex=v2, data=manager.data, graph=bg)
                        sedge_multicolor = s_edge.multicolor if s_edge is not None else Multicolor()
                        for e_scenario_name, e_scenario in non_conflicting_evolutionary_scenarios:
                            evolutionary_scenarios[e_scenario_name] = get_assembly_score(full_ie1_multicolor=full_ie1_multicolor,
                                                                                         full_ie2_multicolor=full_ie2_multicolor,
                                                                                         sedge_multicolor=sedge_multicolor,
                                                                                         target_multicolor=target_multicolor,
                                                                                         evolutionary_scenario=e_scenario,
                                                                                         data=manager.data)

                        api = AssemblyPointInfo(support_edge=s_edge, iedge1=iedge1, iedge2=iedge2,
                                                evolutionary_scenarios=evolutionary_scenarios,
                                                allowed=True, repeat_info=repeat_info, target_multicolor=target_multicolor,
                                                target_color=target_multicolor)
                        ap = AssemblyPoint(vertex1=v1, vertex2=v2, additional_information=api)
                        ap.cc_id = cc_cnt
                        manager.logger.debug("Identified TEMP assembly point :: {ap}".format(ap=ap.as_logger_entry(),
                                                                                             ))

            matching_graph = nx.max_weight_matching(G=possible_assemblies_graph)
            processed_vertices = set()
            for v1, v2 in matching_graph:
                if v1 in processed_vertices or v2 in processed_vertices:
                    continue
                processed_vertices.add(v1)
                processed_vertices.add(v2)
                for color in target_multicolor.colors:
                    iedge1 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v1, color=color)
                    iedge2 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v2, color=color)
                    s_edge = bg.get_condensed_edge(vertex1=v1, vertex2=v2)
                    r1_name, r1_dir = get_repeat_info(iedge1)
                    r2_name, r2_dir = get_repeat_info(iedge2)
                    r1_entry = get_repeat_entry(repeat_name=r1_name, repeat_direction=r1_dir)
                    r2_entry = get_repeat_entry(repeat_name=r2_name, repeat_direction=r2_dir)
                    repeat_info = {
                        "repeat_name_1": r1_name,
                        "repeat_name_2": r2_name,
                        "repeat_dir_1": r1_dir,
                        "repeat_dir_2": r2_dir
                    }
                    try:
                        repeat_guidance = get_repeat_guidance(genome=color, repeat1_entry=r1_entry, repeat2_entry=r2_entry,
                                                              data=manager.data)
                    except nx.networkx.exception.NetworkXNoPath:
                        raise Exception("Pair of edges must suitable for assembly with repeats guidance")
                    repeat_info["repeat_guidance"] = repeat_guidance
                    evolutionary_scenarios = {}
                    full_ie1_multicolor = get_full_irregular_multicolor(vertex=v1, data=manager.data, graph=bg)
                    full_ie2_multicolor = get_full_irregular_multicolor(vertex=v2, data=manager.data, graph=bg)
                    sedge_multicolor = s_edge.multicolor if s_edge is not None else Multicolor()
                    for e_scenario_name, e_scenario in non_conflicting_evolutionary_scenarios:
                        evolutionary_scenarios[e_scenario_name] = get_assembly_score(full_ie1_multicolor=full_ie1_multicolor,
                                                                                     full_ie2_multicolor=full_ie2_multicolor,
                                                                                     sedge_multicolor=sedge_multicolor,
                                                                                     target_multicolor=target_multicolor,
                                                                                     evolutionary_scenario=e_scenario, data=manager.data)

                    api = AssemblyPointInfo(support_edge=s_edge, iedge1=iedge1, iedge2=iedge2,
                                            evolutionary_scenarios=evolutionary_scenarios,
                                            allowed=True, repeat_info=repeat_info, target_multicolor=target_multicolor,
                                            target_color=Multicolor(color))
                    ap = AssemblyPoint(vertex1=v1, vertex2=v2, additional_information=api)
                    ap.cc_id = cc_cnt
                    if not ap_header_printed:
                        ap_header_printed = True
                        manager.logger.debug("-" * 32 + "-" * len(AssemblyPoint.logger_file_header_string()))
                        manager.logger.debug(" " * 32 + AssemblyPoint.logger_file_header_string())
                        manager.logger.debug("-" * 32 + "-" * len(AssemblyPoint.logger_file_header_string()))
                    manager.logger.debug("Identified an assembly point :: {ap}".format(ap=ap.as_logger_entry()))
                    manager.data["gos-asm"]["assembly_points"].append(ap)
                    k_break = create_k_break_from_assembly_point(assembly_point=ap)
                    kbreaks.append(k_break)

        # print(max_cc_size)
        manager.logger.debug("-" * 32 + "-" * len(AssemblyPoint.logger_file_header_string()))
        for k_break in kbreaks:
            bg.apply_kbreak(kbreak=k_break, merge=False)
            assembly_cnt += 1
        manager.logger.info("Identified and performed {gluing_cnt} assemblies with Phylogeny Assembly strategy"
                            "".format(gluing_cnt=assembly_cnt))
        log_bg_stats(bg=bg, logger=manager.logger)
