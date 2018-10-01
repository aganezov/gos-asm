# -*- coding: utf-8 -*-
import itertools

import networkx as nx
from bg.multicolor import Multicolor
from bg.utils import get_from_dict_with_path
from gos.tasks import BaseTask
from networkx import Graph

from gos_asm.algo.data_structures.assemblies import AssemblyPoint, AssemblyPointInfo
from gos_asm.algo.shared.assembly_point import non_conflicting_evolutionary_scenarios, get_assembly_score
from gos_asm.algo.shared.gos_asm_bg import create_k_break_from_assembly_point, get_full_irregular_multicolor, get_balance_graph
from gos_asm.algo.shared.gos_asm_bg import get_repeat_info
from gos_asm.algo.shared.gos_asm_logging import log_bg_stats
from gos_asm.algo.tasks.asm.shared import suitable_for_assembly_fragment_ends_vertex, get_irregular_edge_by_vertex_color, get_repeat_guidance, \
    assembly_is_allowed, get_repeat_entry


class ConnectedComponentAssemblyTask(BaseTask):
    name = "task_CCA"

    def run(self, manager):
        manager.logger.info("=" * 80)
        manager.logger.info("Assembling with Connected Components Assembly strategy")
        manager.logger.info("Strategy version 1")
        bg = manager.data["gos-asm"]["bg"]

        log_bg_stats(bg=bg, logger=manager.logger)
        target_multicolor = manager.data["gos-asm"]["target_multicolor"]
        assembly_cnt = 0
        ap_header_printed = False

        kbreaks = []
        for cc_cnt, cc in enumerate(bg.connected_components_subgraphs(copy=False)):
            possible_assemblies_graph = Graph()
            for vertex in (v for v in cc.nodes() if v.is_regular_vertex):
                if suitable_for_assembly_fragment_ends_vertex(graph=bg, reg_vertex=vertex, target_multicolor=target_multicolor):
                    possible_assemblies_graph.add_node(vertex)
            if len(list(possible_assemblies_graph.nodes())) > 1000:
                continue
            for v1, v2 in itertools.combinations(list(possible_assemblies_graph.nodes()), 2):
                if assembly_is_allowed(graph=bg, vertex1=v1, vertex2=v2, target_multicolor=target_multicolor, data=manager.data):
                    possible_assemblies_graph.add_edge(v1, v2)
            reg_vertices_for_assembly = set()
            for pag_cc in nx.connected_component_subgraphs(possible_assemblies_graph, copy=False):
                if len(list(pag_cc.nodes())) != 2:
                    continue
                reg_vertices_for_assembly.add(tuple(pag_cc.nodes()))

            for vertex_pair in reg_vertices_for_assembly:
                v1, v2 = vertex_pair
                if v1.block_name == v2.block_name:
                    continue
                for color in target_multicolor.colors:
                    iedge1 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v1, color=color)
                    iedge2 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v2, color=color)
                    s_edge = bg.get_condensed_edge(vertex1=v1, vertex2=v2) if bg.has_edge(vertex1=v1, vertex2=v2) else None
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
                        repeat_guidance = get_repeat_guidance(genome=color, repeat1_entry=r1_entry, repeat2_entry=r2_entry, data=manager.data)
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
                        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
                        manager.logger.debug(" "*32 + AssemblyPoint.logger_file_header_string())
                        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
                    manager.logger.debug("Identified an assembly point :: {ap}".format(ap=ap.as_logger_entry()))
                    manager.data["gos-asm"]["assembly_points"].append(ap)
                    k_break = create_k_break_from_assembly_point(assembly_point=ap)
                    kbreaks.append(k_break)
        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
        for k_break in kbreaks:
            bg.apply_kbreak(kbreak=k_break, merge=False)
            assembly_cnt += 1
        manager.logger.info("Identified and performed {gluing_cnt} assemblies with Connected Components Assembly strategy"
                            "".format(gluing_cnt=assembly_cnt))
        log_bg_stats(bg=bg, logger=manager.logger)


class ConnectedComponentAssemblyTaskBalanced(BaseTask):
    name = "task_CCA_balanced"

    def run(self, manager):
        manager.logger.info("=" * 80)
        manager.logger.info("Assembling with Connected Components Assembly strategy")
        manager.logger.info("Strategy version 1")
        bg = manager.data["gos-asm"]["bg"]

        log_bg_stats(bg=bg, logger=manager.logger)
        target_multicolor = manager.data["gos-asm"]["target_multicolor"]
        assembly_cnt = 0
        ap_header_printed = False

        kbreaks = []
        guidance_graph = get_balance_graph(bg)
        log_bg_stats(bg=guidance_graph, logger=manager.logger)
        for cc_cnt, cc in enumerate(guidance_graph.connected_components_subgraphs(copy=False)):
            possible_assemblies_graph = Graph()
            for vertex in (v for v in cc.nodes() if v.is_regular_vertex):
                if suitable_for_assembly_fragment_ends_vertex(graph=bg, reg_vertex=vertex, target_multicolor=target_multicolor):
                    possible_assemblies_graph.add_node(vertex)
            if len(list(possible_assemblies_graph.nodes())) > 1000:
                continue
            for v1, v2 in itertools.combinations(list(possible_assemblies_graph.nodes()), 2):
                if assembly_is_allowed(graph=bg, vertex1=v1, vertex2=v2, target_multicolor=target_multicolor, data=manager.data):
                    possible_assemblies_graph.add_edge(v1, v2)
            reg_vertices_for_assembly = set()
            for pag_cc in nx.connected_component_subgraphs(possible_assemblies_graph, copy=False):
                if len(list(pag_cc.nodes())) != 2:
                    continue
                reg_vertices_for_assembly.add(tuple(pag_cc.nodes()))

            for vertex_pair in reg_vertices_for_assembly:
                v1, v2 = vertex_pair
                if v1.block_name == v2.block_name:
                    continue
                for color in target_multicolor.colors:
                    iedge1 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v1, color=color)
                    iedge2 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v2, color=color)
                    fr1_name = get_from_dict_with_path(iedge1.data, key="name", path=["fragment"])
                    fr2_name = get_from_dict_with_path(iedge2.data, key='name', path=["fragment"])
                    if fr1_name == fr2_name:
                        continue
                    s_edge = bg.get_condensed_edge(vertex1=v1, vertex2=v2) if bg.has_edge(vertex1=v1, vertex2=v2) else None
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
                        repeat_guidance = get_repeat_guidance(genome=color, repeat1_entry=r1_entry, repeat2_entry=r2_entry, data=manager.data)
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
                        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
                        manager.logger.debug(" "*32 + AssemblyPoint.logger_file_header_string())
                        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
                    manager.logger.debug("Identified an assembly point :: {ap}".format(ap=ap.as_logger_entry()))
                    manager.data["gos-asm"]["assembly_points"].append(ap)
                    k_break = create_k_break_from_assembly_point(assembly_point=ap)
                    kbreaks.append(k_break)
        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
        for k_break in kbreaks:
            bg.apply_kbreak(kbreak=k_break, merge=False)
            assembly_cnt += 1
        manager.logger.info("Identified and performed {gluing_cnt} assemblies with Connected Components Assembly strategy"
                            "".format(gluing_cnt=assembly_cnt))
        log_bg_stats(bg=bg, logger=manager.logger)


class MGRAConnectedComponentAssemblyTask(BaseTask):
    name = "task_CCA_MGRA"

    def run(self, manager):
        manager.logger.info("=" * 80)
        manager.logger.info("Assembling with Connected Components Assembly Strategy Using MGRA guidance graph")
        manager.logger.info("Strategy version 2")
        bg = manager.data["gos-asm"]["bg"]
        guidance_graph = manager.data["mgra"]["guidance_graph"]

        log_bg_stats(bg=bg, logger=manager.logger)
        target_multicolor = manager.data["gos-asm"]["target_multicolor"]
        assembly_cnt = 0
        ap_header_printed = False

        kbreaks = []
        for cc_cnt, cc in enumerate(guidance_graph.connected_components_subgraphs(copy=False)):
            possible_assemblies_graph = Graph()
            for vertex in (v for v in cc.nodes() if v.is_regular_vertex):
                if suitable_for_assembly_fragment_ends_vertex(graph=bg, reg_vertex=vertex, target_multicolor=target_multicolor):
                    possible_assemblies_graph.add_node(vertex)
            if len(list(possible_assemblies_graph.nodes())) > 1000:
                continue
            for v1, v2 in itertools.combinations(list(possible_assemblies_graph.nodes()), 2):
                if assembly_is_allowed(graph=bg, vertex1=v1, vertex2=v2, target_multicolor=target_multicolor, data=manager.data):
                    possible_assemblies_graph.add_edge(v1, v2)
            reg_vertices_for_assembly = set()
            for pag_cc in nx.connected_component_subgraphs(possible_assemblies_graph, copy=False):
                if len(list(pag_cc.nodes())) != 2:
                    continue
                reg_vertices_for_assembly.add(tuple(pag_cc.nodes()))

            for vertex_pair in reg_vertices_for_assembly:
                v1, v2 = vertex_pair
                if v1.block_name == v2.block_name:
                    continue
                for color in target_multicolor.colors:
                    iedge1 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v1, color=color)
                    iedge2 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v2, color=color)

                    s_edge = bg.get_condensed_edge(vertex1=v1, vertex2=v2) if bg.has_edge(vertex1=v1, vertex2=v2) else None
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
                        repeat_guidance = get_repeat_guidance(genome=color, repeat1_entry=r1_entry, repeat2_entry=r2_entry, data=manager.data)
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
                        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
                        manager.logger.debug(" "*32 + AssemblyPoint.logger_file_header_string())
                        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
                    manager.logger.debug("Identified an assembly point :: {ap}".format(ap=ap.as_logger_entry()))
                    manager.data["gos-asm"]["assembly_points"].append(ap)
                    k_break = create_k_break_from_assembly_point(assembly_point=ap)
                    kbreaks.append(k_break)
        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
        for k_break in kbreaks:
            bg.apply_kbreak(kbreak=k_break, merge=False)
            assembly_cnt += 1
        manager.logger.info("Identified and performed {gluing_cnt} assemblies with Connected Components Assembly strategy"
                            "".format(gluing_cnt=assembly_cnt))
        log_bg_stats(bg=bg, logger=manager.logger)


class MGRAConnectedComponentAssemblyTaskBalanced(BaseTask):
    name = "task_CCA_MGRA_balanced"

    def run(self, manager):
        manager.logger.info("=" * 80)
        manager.logger.info("Assembling with Connected Components Assembly Strategy Using MGRA guidance graph")
        manager.logger.info("Strategy version 2")
        bg = manager.data["gos-asm"]["bg"]
        guidance_graph = manager.data["mgra"]["guidance_graph"]
        guidance_graph = get_balance_graph(breakpoint_graph=guidance_graph)

        log_bg_stats(bg=bg, logger=manager.logger)
        log_bg_stats(bg=guidance_graph, logger=manager.logger)
        target_multicolor = manager.data["gos-asm"]["target_multicolor"]
        assembly_cnt = 0
        ap_header_printed = False

        kbreaks = []
        for cc_cnt, cc in enumerate(guidance_graph.connected_components_subgraphs(copy=False)):
            possible_assemblies_graph = Graph()
            for vertex in (v for v in cc.nodes() if v.is_regular_vertex):
                if suitable_for_assembly_fragment_ends_vertex(graph=bg, reg_vertex=vertex, target_multicolor=target_multicolor):
                    possible_assemblies_graph.add_node(vertex)
            if len(list(possible_assemblies_graph.nodes())) > 1000:
                continue
            for v1, v2 in itertools.combinations(list(possible_assemblies_graph.nodes()), 2):
                if assembly_is_allowed(graph=bg, vertex1=v1, vertex2=v2, target_multicolor=target_multicolor, data=manager.data):
                    possible_assemblies_graph.add_edge(v1, v2)
            reg_vertices_for_assembly = set()
            for pag_cc in nx.connected_component_subgraphs(possible_assemblies_graph, copy=False):
                if len(list(pag_cc.nodes())) != 2:
                    continue
                reg_vertices_for_assembly.add(tuple(pag_cc.nodes()))

            for vertex_pair in reg_vertices_for_assembly:
                v1, v2 = vertex_pair
                if v1.block_name == v2.block_name:
                    continue
                for color in target_multicolor.colors:
                    iedge1 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v1, color=color)
                    iedge2 = get_irregular_edge_by_vertex_color(graph=bg, vertex=v2, color=color)
                    fr1_name = get_from_dict_with_path(iedge1.data, key="name", path=["fragment"])
                    fr2_name = get_from_dict_with_path(iedge2.data, key='name', path=["fragment"])
                    if fr1_name == fr2_name:
                        continue
                    s_edge = bg.get_condensed_edge(vertex1=v1, vertex2=v2) if bg.has_edge(vertex1=v1, vertex2=v2) else None
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
                        repeat_guidance = get_repeat_guidance(genome=color, repeat1_entry=r1_entry, repeat2_entry=r2_entry, data=manager.data)
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
                        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
                        manager.logger.debug(" "*32 + AssemblyPoint.logger_file_header_string())
                        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
                    manager.logger.debug("Identified an assembly point :: {ap}".format(ap=ap.as_logger_entry()))
                    manager.data["gos-asm"]["assembly_points"].append(ap)
                    k_break = create_k_break_from_assembly_point(assembly_point=ap)
                    kbreaks.append(k_break)
        manager.logger.debug("-"*32 + "-"*len(AssemblyPoint.logger_file_header_string()))
        for k_break in kbreaks:
            bg.apply_kbreak(kbreak=k_break, merge=False)
            assembly_cnt += 1
        manager.logger.info("Identified and performed {gluing_cnt} assemblies with Connected Components Assembly strategy"
                            "".format(gluing_cnt=assembly_cnt))
        log_bg_stats(bg=bg, logger=manager.logger)