# -*- coding: utf-8 -*-
from algo.shared.logging import log_bg_stats
from bg import BreakpointGraph, Multicolor, BGGenome
from bg.bg_io import GRIMMReader
from bg.tree import NewickReader
from gos.tasks import BaseTask


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

        # manager.logger.info("Reading repeats-bridges information")

