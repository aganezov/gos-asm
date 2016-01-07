# -*- coding: utf-8 -*-
import itertools

from algo.shared.logging import log_bg_stats
from bg import Multicolor
from collections import defaultdict
from gos.tasks import BaseTask
from gos_asm.algo.data_structures.assemblies import AssemblyPoint, AssemblyPointInfo
from gos_asm.algo.shared.assembly_point import get_assembly_point_info, non_conflicting_evolutionary_scenarios, get_assembly_score
from gos_asm.algo.shared.bg import create_k_break_from_assembly_point, get_regular_vertex, get_full_irregular_multicolor
from gos_asm.algo.shared.bg import get_repeat_info
from networkx import Graph
import networkx as nx


def suitable_for_assembly_fragment_ends_vertex(graph, reg_vertex, target_multicolor):
    fimc = get_full_irregular_multicolor(vertex=reg_vertex, data=None, graph=graph)
    return target_multicolor <= fimc and not any(map(lambda color: fimc.multicolors[color] > 1, target_multicolor.colors))


def get_irregular_edge_by_vertex_color(graph, vertex, color):
    for edge in graph.get_edges_by_vertex(vertex=vertex):
        if edge.is_irregular_edge and color in edge.multicolor.colors:
            return edge
    return None


def get_repeat_guidance(genome, repeat1_entry, repeat2_entry, data):
    try:
        source = str(repeat1_entry) + "ou"
        target = str(repeat2_entry) + "oi"
        repeats_matching_graph = data["gos-asm"]["repeats_guidance"][genome]
        return nx.shortest_path(G=repeats_matching_graph, source=source, target=target)
    except nx.networkx.exception.NetworkXNoPath:
        raise


def repeats_are_matching(genome, repeat1_entry, repeat2_entry, data):
    try:
        get_repeat_guidance(genome=genome, repeat1_entry=repeat1_entry, repeat2_entry=repeat2_entry, data=data)
        return True
    except nx.networkx.exception.NetworkXNoPath:
        return False


def assembly_is_allowed(graph, vertex1, vertex2, target_multicolor, data):
    result = True
    for color in target_multicolor.colors:
        iedge1 = get_irregular_edge_by_vertex_color(graph=graph, vertex=vertex1, color=color)
        iedge2 = get_irregular_edge_by_vertex_color(graph=graph, vertex=vertex2, color=color)
        ie1rn, ie1rd = get_repeat_info(iedge1)
        ie2rn, ie2rd = get_repeat_info(iedge2)
        ie1r_entry = get_repeat_entry(repeat_direction=ie1rd, repeat_name=ie1rn)
        ie2r_entry = get_repeat_entry(repeat_direction=ie2rd, repeat_name=ie2rn)
        result &= repeats_are_matching(genome=color, repeat1_entry=ie1r_entry, repeat2_entry=ie2r_entry, data=data)
    return result


def get_repeat_entry(repeat_name, repeat_direction):
    return None if any(map(lambda v: v is None, [repeat_direction, repeat_name])) else repeat_name + repeat_direction


class ConnectedComponentAssemblyTask(BaseTask):
    name = "task_CCA"

    def run(self, manager):
        manager.logger.info("=" * 80)
        manager.logger.info("Assembling with Connected Components Assembly strategy")
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


class MGRAConnectedComponentAssemblyTask(BaseTask):
    name = "task_CCA_MGRA"

    def run(self, manager):
        manager.logger.info("=" * 80)
        manager.logger.info("Assembling with Connected Components Assembly strategy")
        bg = manager.data["gos-asm"]["bg"]

        log_bg_stats(bg=bg, logger=manager.logger)
        target_multicolor = manager.data["gos-asm"]["target_multicolor"]
        assembly_cnt = 0

        kbreaks = []
        for cc in bg.connected_components_subgraphs(copy=False):
            repeat_edges = defaultdict(list)
            non_repeat_edges = []

            # looking only at irregular edges
            irregular_edges = (edge for edge in cc.edges() if edge.is_irregular_edge)
            # looking at irregular edges that have target multicolor
            target_irregular_edges = (edge for edge in irregular_edges if target_multicolor <= edge.multicolor)
            # looking at irregular edges that don't have duplications from target multicolor perspective
            target_irregular_edges = (edge for edge in target_irregular_edges
                                      if not any(map(lambda color: edge.multicolor.multicolors[color] > 1, target_multicolor.colors)))

            for edge in target_irregular_edges:
                if edge.is_repeat_edge:
                    repeat_name, _ = get_repeat_info(edge)
                    repeat_edges[repeat_name].append(edge)
                else:
                    non_repeat_edges.append(edge)

            edges_groups = [edges_group for edges_group in repeat_edges.values()]

            for edges_group in edges_groups:
                if len(edges_group) != 2:
                    continue
                edge1, edge2 = edges_group
                vertex1 = edge1.vertex1 if edge1.vertex1.is_regular_vertex else edge1.vertex2
                vertex2 = edge2.vertex1 if edge2.vertex1.is_regular_vertex else edge2.vertex2
                assembly_point_info = get_assembly_point_info(iedge1=edge1,
                                                              iedge2=edge2,
                                                              data=manager.data)
                assembly_point = AssemblyPoint(vertex1=vertex1, vertex2=vertex2,
                                               additional_information=assembly_point_info)
                manager.logger.debug("Identified an assembly point :: {ap}".format(ap=str(assembly_point)))
                manager.data["gos-asm"]["assembly_points"].append(assembly_point)
                k_break = create_k_break_from_assembly_point(assembly_point=assembly_point)
                kbreaks.append(k_break)
        for k_break in kbreaks:
            bg.apply_kbreak(kbreak=k_break)
            assembly_cnt += 1
        manager.logger.info("Identified and performed {gluing_cnt} assemblies with Connected Components Assembly strategy"
                            "".format(gluing_cnt=assembly_cnt))
        log_bg_stats(bg=bg, logger=manager.logger)
