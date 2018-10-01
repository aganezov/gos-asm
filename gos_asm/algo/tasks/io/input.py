# -*- coding: utf-8 -*-

import os
from copy import deepcopy

from bg.breakpoint_graph import BreakpointGraph
from bg.genome import BGGenome
from bg.grimm import GRIMMReader
from bg.multicolor import Multicolor
from bg.tree import BGTree
from gos.tasks import BaseTask
from networkx import DiGraph

from gos_asm.algo.shared.gos_asm_bg import iter_over_all_repeats


def get_repeats_bridges_guidance(file_name, data):
    result = {}
    opposite_dirs = {
        "h": "t",
        "t": "h"
    }
    bg = data["gos-asm"]["bg"]
    for genome in bg.get_overall_set_of_colors():
        result[genome] = DiGraph()
        result[genome].add_edge(str(None) + "ou", str(None) + "oi")
        for repeat_name, r_dir in iter_over_all_repeats(bg=bg, multicolor=Multicolor(genome)):
            rou = repeat_name + r_dir + "ou"
            roi = repeat_name + opposite_dirs[r_dir] + "oi"
            result[genome].add_edge(rou, roi)
            rou = repeat_name + opposite_dirs[r_dir] + "ou"
            roi = repeat_name + r_dir + "oi"
            result[genome].add_edge(rou, roi)
    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        return result
    current_genome = None
    with open(file_name, "rt") as source:
        for cnt, line in enumerate(source):
            if len(line.strip()) == 0 and line.strip().startswith("#"):
                continue
            elif line.strip().startswith(">"):
                current_genome = BGGenome(line.strip()[1:])
            else:
                data = line.strip().split()
                if len(data) != 2:
                    continue
                r1_data, r2_data = map(lambda entry: entry.split("__"), data)
                r1_base, r2_base = r1_data[0], r2_data[0]
                r1_sign = "-" if r1_base.startswith("-") else "+"
                r2_sign = "-" if r2_base.startswith("-") else "+"
                r1_name = r1_base[1:] if r1_base.startswith("-") else r1_base
                r2_name = r2_base[1:] if r2_base.startswith("-") else r2_base
                r1_suffix = "h" if r1_sign == "+" else "t"
                r2_suffix = "t" if r2_sign == "+" else "h"
                source = r1_name + r1_suffix + "oi"
                target = r2_name + r2_suffix + "ou"
                if current_genome is not None:
                    result[current_genome].add_edge(source, target)
    return result


class Input(BaseTask):
    name = "task_input"

    def run(self, manager):
        manager.logger.info("Reading blocks orders data")
        file_paths = manager.configuration["gos-asm"]["input"]["block_orders_file_paths"]
        bg = BreakpointGraph()
        for file_path in file_paths:
            with open(file_path, "rt") as source:
                bg.update(breakpoint_graph=GRIMMReader.get_breakpoint_graph(stream=source, merge_edges=False), merge_edges=False)
        manager.data["gos-asm"]["bg"] = bg

        manager.logger.info("Reading phylogenetic tree information")
        tree = BGTree(newick=manager.configuration["gos-asm"]["input"]["phylogenetic_tree"])
        manager.data["gos-asm"]["phylogenetic_tree"] = tree

        full_tmc = Multicolor(*[BGGenome(genome_name) for genome_name in manager.configuration["gos-asm"]["input"]["target_organisms"]])
        manager.data["gos-asm"]["target_multicolor"] = full_tmc
        vtree_consistent_target_multicolors = Multicolor.split_colors(full_tmc,
                                                                      guidance=tree.vtree_consistent_multicolors,
                                                                      account_for_color_multiplicity_in_guidance=False)

        for target_multicolor in vtree_consistent_target_multicolors[:]:
            for vtree_c_multicolor in deepcopy(tree.vtree_consistent_multicolors):
                if vtree_c_multicolor <= target_multicolor \
                        and vtree_c_multicolor not in vtree_consistent_target_multicolors \
                        and len(vtree_c_multicolor.colors) > 0:
                    vtree_consistent_target_multicolors.append(vtree_c_multicolor)

        vtree_consistent_target_multicolors = sorted(vtree_consistent_target_multicolors,
                                                     key=lambda mc: len(mc.hashable_representation),
                                                     reverse=True)

        all_target_multicolors = vtree_consistent_target_multicolors[:]
        # for i in range(2, len(vtree_consistent_target_multicolors) + 1):
        #     for comb in itertools.combinations(vtree_consistent_target_multicolors[:], i):
        #         comb = list(comb)
        #         for mc1, mc2 in itertools.combinations(comb, 2):
        #             if len(mc1.intersect(mc2).colors) > 0:
        #                 break
        #         else:
        #             new_mc = Multicolor()
        #             for mc in comb:
        #                 new_mc += mc
        #             all_target_multicolors.append(new_mc)
        hashed_vertex_tree_consistent_multicolors = {mc.hashable_representation for mc in all_target_multicolors}
        all_target_multicolors = [Multicolor(*hashed_multicolor) for hashed_multicolor in
                                  hashed_vertex_tree_consistent_multicolors]
        all_target_multicolors = sorted(all_target_multicolors,
                                        key=lambda mc: len(mc.hashable_representation),
                                        reverse=True)
        manager.data["gos-asm"]["target_multicolors"] = all_target_multicolors
        # log_bg_stats(bg=bg, logger=manager.logger)

        manager.logger.info("Reading repeats-bridges information")
        manager.data["gos-asm"]["repeats_guidance"] = get_repeats_bridges_guidance(
            file_name=manager.configuration["gos-asm"]["input"]["repeats_bridges_file"], data=manager.data)
