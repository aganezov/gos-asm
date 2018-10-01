# -*- coding: utf-8 -*-
import json
import os

from bg.breakpoint_graph import BreakpointGraph
from bg.grimm import GRIMMWriter, GRIMMReader
from bg.utils import get_from_dict_with_path
from gos.tasks import BaseTask


class ObtainGuidanceGraph(BaseTask):
    name = "task_GG_MGRA"

    def create_mgra_config(self, blocks_file_name, manager):
        result = {}
        genomes = []
        overall_set_of_colors = manager.data["gos-asm"]["bg"].get_overall_set_of_colors()
        for bggenome in overall_set_of_colors:
            genomes.append({
                "priority_name": bggenome.name
            })
        result["genomes"] = genomes
        result["format_of_blocks"] = "grimm"
        result["files"] = [os.path.basename(blocks_file_name)]
        result["trees"] = [
            manager.configuration["gos-asm"]["input"]["phylogenetic_tree"].replace(" ", "")
        ]
        result["algorithm"] = {
            "rounds": 1,
            "stages": [
                "balance",
                "simple_path",
                "fair_edge",
                "components"
            ]
        }
        return result

    def run(self, manager):
        mgra_ex_path = get_from_dict_with_path(manager.configuration, key="executable_path", path=["mgra"])
        manager.logger.info("=" * 80)
        if mgra_ex_path is None:
            manager.logger.info("MGRA executable path is not supplied, skipping the MGRA based tasks")
            return
        manager.logger.info("Preparing data to communicate with MGRA and ontain guidance graph")
        temp_dir = os.path.join(manager.configuration["gos-asm"]["output"]["dir"], "tmp_mgra")
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        blocks_file_name = os.path.join(temp_dir, "blocks.txt")
        config_file_name = os.path.join(temp_dir, "config.cfg")
        mgra_output_dir_name = os.path.join(temp_dir, "output/")

        manager.logger.debug("Writing blocks orders in GRIMM format to {file_name}".format(file_name=blocks_file_name))
        GRIMMWriter.print_genomes_as_grimm_blocks_orders(bg=manager.data["gos-asm"]["bg"],
                                                         file_name=blocks_file_name)

        manager.logger.debug("Writing configuration file for MGRA run to {file_name}".format(file_name=config_file_name))
        config = self.create_mgra_config(blocks_file_name=blocks_file_name, manager=manager)
        with open(config_file_name, "wt") as destination:
            json.dump(obj=config, fp=destination)
        manager.logger.info("Running MGRA on prepared configuration")
        os.system("{mgra_ex_path} -c {config_file_path} -o {output_dir_path}"
                  "".format(mgra_ex_path=mgra_ex_path,
                            config_file_path=config_file_name,
                            output_dir_path=mgra_output_dir_name))
        manager.logger.debug("MGRA has successfully finished")
        manager.logger.info("Reading MGRA produced guidance graph")

        genomes_dir = os.path.join(mgra_output_dir_name, "genomes")
        genome_files = [name for name in os.listdir(genomes_dir) if name.endswith(".gen")]
        full_genomes_paths = [os.path.join(genomes_dir, name) for name in genome_files]
        guidance_bg = BreakpointGraph()
        for file_name in full_genomes_paths:
            with open(file_name, "rt") as source:
                guidance_bg.update(breakpoint_graph=GRIMMReader.get_breakpoint_graph(stream=source, merge_edges=False), merge_edges=False)
        if "mgra" not in manager.data:
            manager.data["mgra"] = {}
        manager.data["mgra"]["guidance_graph"] = guidance_bg
        manager.logger.info("Obtained MGRA produced guidance graph")
