# -*- coding: utf-8 -*-
from algo.shared.logging import log_bg_stats
from collections import defaultdict
from gos.tasks import BaseTask
from gos_asm.algo.data_structures.assemblies import AssemblyPoint
from gos_asm.algo.shared.assembly_point import get_assembly_point_info
from gos_asm.algo.shared.bg import create_k_break_from_assembly_point, get_regular_vertex, get_full_irregular_multicolor
from gos_asm.algo.shared.bg import get_repeat_info


class ConnectedComponentAssemblyTask(BaseTask):
    name = "task_CCA"

    def run(self, manager):
        manager.logger.info("=" * 80)
        manager.logger.info("Assembling with Connected Components Assembly strategy")
        bg = manager.data["gos-asm"]["bg"]

        log_bg_stats(bg=bg, logger=manager.logger)
        target_multicolor = manager.data["gos-asm"]["target_multicolor"]
        assembly_cnt = 0

        kbreaks = []
        for cc_cnt, cc in enumerate(bg.connected_components_subgraphs(copy=False)):
            repeat_edges = defaultdict(list)
            non_repeat_edges = []

            # looking only at irregular edges
            irregular_edges = (edge for edge in cc.edges() if edge.is_irregular_edge)
            # looking at irregular edges that have target multicolor
            target_irregular_edges = (edge for edge in irregular_edges if target_multicolor <= edge.multicolor)
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
                assembly_point.cc_id=cc_cnt
                manager.logger.debug("Identified an assembly point :: {ap}".format(ap=assembly_point.as_logger_entry()))
                manager.data["gos-asm"]["assembly_points"].append(assembly_point)
                k_break = create_k_break_from_assembly_point(assembly_point=assembly_point)
                kbreaks.append(k_break)
        for k_break in kbreaks:
            bg.apply_kbreak(kbreak=k_break)
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