# -*- coding: utf-8 -*-
import networkx as nx

from gos_asm.algo.shared.gos_asm_bg import get_full_irregular_multicolor, get_repeat_info


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