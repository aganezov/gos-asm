# -*- coding: utf-8 -*-
import os

from algo.shared.bg import iter_over_all_repeats
from algo.shared.logging import log_bg_stats
from bg import BreakpointGraph, Multicolor, BGGenome
from bg.bg_io import GRIMMReader
from bg.tree import NewickReader
from gos.tasks import BaseTask
from networkx import Graph, DiGraph


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
                bg.update(breakpoint_graph=GRIMMReader.get_breakpoint_graph(stream=source), merge_edges=True)
        manager.data["gos-asm"]["bg"] = bg

        manager.logger.info("Reading phylogenetic tree information")
        tree = NewickReader.from_string(data_string=manager.configuration["gos-asm"]["input"]["phylogenetic_tree"])
        manager.data["gos-asm"]["phylogenetic_tree"] = tree

        manager.data["gos-asm"]["target_multicolor"] = Multicolor(*[BGGenome(genome_name) for genome_name in manager.configuration["gos-asm"]["input"]["target_organisms"]])
        log_bg_stats(bg=bg, logger=manager.logger)

        manager.logger.info("Reading repeats-bridges information")
        manager.data["gos-asm"]["repeats_guidance"] = get_repeats_bridges_guidance(file_name=manager.configuration["gos-asm"]["input"]["repeats_bridges_file"], data=manager.data)
