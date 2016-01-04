# -*- coding: utf-8 -*-
from bg import Multicolor, BGEdge, KBreak


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


def get_full_irregular_multicolor(vertex, data):
    result = Multicolor()
    bg = data["gos-asm"]["bg"]
    for edge in bg.get_edges_by_vertex(vertex):
        if edge.is_irregular_edge:
            result += edge.multicolor
    return result


def create_k_break_from_assembly_point(assembly_point):
    v1, v2 = get_regular_vertex(assembly_point.info.iedge1), get_irregular_vertex(assembly_point.info.iedge1)
    v3, v4 = get_regular_vertex(assembly_point.info.iedge2), get_irregular_vertex(assembly_point.info.iedge2)

    return KBreak(start_edges=[(v1, v2), (v3, v4)],
                  result_edges=[(v1, v3), (v2, v4)],
                  multicolor=assembly_point.target_multicolor)
