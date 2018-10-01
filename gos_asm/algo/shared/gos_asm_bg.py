# -*- coding: utf-8 -*-
from bg.multicolor import Multicolor
from bg.edge import BGEdge
from bg.kbreak import KBreak
from bg.breakpoint_graph import BreakpointGraph


def has_edge_between_two_vertices(vertex1, vertex2, data):
    bg = data["gos-asm"]["bg"]
    try:
        bg.edges_between_two_vertices(vertex1=vertex1, vertex2=vertex2)
        return True
    except ValueError:
        return False


def get_irregular_vertex(bgedge):
    """
    This method is called only in irregular edges in current implementation, thus at least one edge will be irregular
    """
    if not bgedge.is_irregular_edge:
        raise Exception("trying to retrieve an irregular vertex from regular edge")
    return bgedge.vertex1 if bgedge.vertex1.is_irregular_vertex else bgedge.vertex2


def get_repeat_info(iedge1):
    if iedge1.is_repeat_edge:
        repeat = [value for tag, value in get_irregular_vertex(iedge1).tags if tag == "repeat"][0]
        return repeat[:-1], repeat[-1]
    else:
        return None, None


def get_full_support_edge(regular_vertex1, regular_vertex2, data):
    bg = data["gos-asm"]["bg"]
    multicolor = Multicolor(*[color for bgedge in bg.edges_between_two_vertices(vertex1=regular_vertex1, vertex2=regular_vertex2) for color in
                            bgedge.multicolor.colors])
    return BGEdge(vertex1=regular_vertex1, vertex2=regular_vertex2, multicolor=multicolor)


def get_regular_vertex(iedge):
    return iedge.vertex1 if iedge.vertex1.is_regular_vertex else iedge.vertex2


def get_full_irregular_multicolor(vertex, data, graph=None):
    result = Multicolor()
    if graph is None:
        bg = data["gos-asm"]["bg"]
    else:
        bg = graph
    for edge in bg.get_edges_by_vertex(vertex):
        if edge.is_irregular_edge:
            result += edge.multicolor
    return result


def create_k_break_from_assembly_point(assembly_point):
    v1, v2 = get_regular_vertex(assembly_point.info.iedge1), get_irregular_vertex(assembly_point.info.iedge1)
    v3, v4 = get_regular_vertex(assembly_point.info.iedge2), get_irregular_vertex(assembly_point.info.iedge2)

    return KBreak(start_edges=[(v1, v2), (v3, v4)],
                  result_edges=[(v1, v3), (v2, v4)],
                  multicolor=assembly_point.info.target_color)


def get_overall_repeats(bg):
    pass


def iter_over_all_repeats(bg, multicolor):
    for edge in bg.edges():
        if edge.is_repeat_edge and multicolor <= edge.multicolor:
            yield get_repeat_info(edge)


def get_overall_incident_from_vertex(bg, vertex):
    result = Multicolor()
    for edge in bg.get_edges_by_vertex(vertex):
        result += edge.multicolor
    return result


def get_balance_graph(breakpoint_graph):
    result = BreakpointGraph()
    result.update(breakpoint_graph, merge_edges=False)
    overall_multicolor = Multicolor(*breakpoint_graph.get_overall_set_of_colors())
    balanced = set()
    for vertex in (v for v in breakpoint_graph.nodes() if v.is_regular_vertex):
        vertex_multicolor = get_overall_incident_from_vertex(bg=breakpoint_graph, vertex=vertex)
        missing_multicolor = overall_multicolor - vertex_multicolor
        if len(missing_multicolor.colors) > 0:
            if vertex in balanced:
                continue
            for color in missing_multicolor.colors:
                mc = Multicolor(color)
                result.add_edge(vertex1=vertex, vertex2=vertex.mate_vertex, multicolor=mc,
                                merge=False)
            balanced.add(vertex)
            balanced.add(vertex.mate_vertex)
    return result
