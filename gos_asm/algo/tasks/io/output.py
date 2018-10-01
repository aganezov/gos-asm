# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from gos.tasks import BaseTask

from gos_asm.algo.data_structures.assemblies import AssemblyPoint


class Output(BaseTask):
    name = "task_output"

    def run(self, manager):
        output_dir = manager.configuration["gos-asm"]["output"]["dir"]

        output_chains = manager.configuration["gos-asm"]["output"]["output_chains"]
        chains_file_name = manager.configuration["gos-asm"]["output"]["chains_file"]
        full_chains_file_path = os.path.join(output_dir, chains_file_name)

        output_filtered_chains = manager.configuration["gos-asm"]["output"]["output_filtered_chains"]
        filtered_chains_file = manager.configuration["gos-asm"]["output"]["filtered_chains_file"]
        full_filtered_chains_file = os.path.join(output_dir, filtered_chains_file)

        assembly_points_file_name = manager.configuration["gos-asm"]["output"]["assembly_points_file"]
        full_assembly_points_file_path = os.path.join(output_dir, assembly_points_file_name)

        manager.logger.info("Writing information about {ap_cnt} identified assembly points into {file_name}"
                            "".format(file_name=full_assembly_points_file_path,
                                      ap_cnt=len(manager.data["gos-asm"]["assembly_points"])))
        with open(full_assembly_points_file_path, "wt") as assembly_points_destination:
            print(AssemblyPoint.assembly_file_header_string(), file=assembly_points_destination)
            for ap in manager.data["gos-asm"]["assembly_points"]:
                print(ap.as_assembly_points_file_entry_string(), file=assembly_points_destination)

        if output_chains:
            manager.logger.info("Writing information about fragments in targeted for assembly genomes into file {file_name}"
                                "".format(file_name=full_chains_file_path))
            bg = manager.data["gos-asm"]["bg"]
            with open(full_chains_file_path, "wt") as chains_destination:
                for genome in bg.get_overall_set_of_colors():
                    if genome.name not in manager.configuration["gos-asm"]["input"]["target_organisms"]:
                        continue
                    genome_graph = bg.get_genome_graph(color=genome)
                    fragments_orders = genome_graph.get_fragments_orders()
                    fragments_orders = fragments_orders[genome]
                    if len(fragments_orders) > 0 and any(map(lambda entry: len(entry[1]) > 0, fragments_orders)):
                        print(">{genome_name}".format(genome_name=genome.name), file=chains_destination)
                    for chr_type, fragments_order in fragments_orders:
                        string = " ".join(value if sign == "+" else (sign + value) for sign, value in fragments_order)
                        string += " {chr_type}".format(chr_type=chr_type)
                        print(string, file=chains_destination)

        if output_filtered_chains:
            manager.logger.info("Writing information about \"chained\" fragments in targeted for assembly genomes into file {file_name}"
                                "".format(file_name=full_chains_file_path))
            bg = manager.data["gos-asm"]["bg"]
            with open(full_filtered_chains_file, "wt") as filtered_chains_destination:
                for genome in bg.get_overall_set_of_colors():
                    if genome.name not in manager.configuration["gos-asm"]["input"]["target_organisms"]:
                        continue
                    genome_graph = bg.get_genome_graph(color=genome)
                    fragments_orders = genome_graph.get_fragments_orders()
                    fragments_orders = fragments_orders[genome]
                    if len(fragments_orders) > 0 and any(map(lambda entry: len(entry[1]) > 1, fragments_orders)):
                        print(">{genome_name}".format(genome_name=genome.name), file=filtered_chains_destination)
                    for chr_type, fragments_order in fragments_orders:
                        if len(fragments_order) == 1:
                            continue
                        string = " ".join(value if sign == "+" else (sign + value) for sign, value in fragments_order)
                        string += " {chr_type}".format(chr_type=chr_type)
                        print(string, file=filtered_chains_destination)
