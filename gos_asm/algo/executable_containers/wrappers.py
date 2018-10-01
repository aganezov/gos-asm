# -*- coding: utf-8 -*-
from gos.executable_containers import ExecutableContainer


def string_representation_of_multicolor(multicolor):
    return ", ".join(color.name for color in sorted(multicolor.colors))


class TargetMulticolorSwitcher(ExecutableContainer):
    name = 'tmc_wrapper'

    def run(self, manager):
        manager.logger.info("="*80)
        manager.logger.info(
            "Total # of targeted for assembling multicolors: {tm_cnt}".format(tm_cnt=len(manager.data["gos-asm"]["target_multicolors"])))
        for tmc in manager.data["gos-asm"]["target_multicolors"]:
            manager.logger.info("{tmc}".format(tmc=string_representation_of_multicolor(tmc)))
        for tmc in manager.data["gos-asm"]["target_multicolors"]:
            manager.logger.info("="*80)
            manager.logger.info("Current multicolor for assembling is: {color}".format(color=", ".join(color.name for color in tmc.colors)))
            manager.data["gos-asm"]["target_multicolor"] = tmc
            super(TargetMulticolorSwitcher, self).run(manager=manager)


class TargetMulticolorSwitcherCCA(TargetMulticolorSwitcher):
    name = 'tmc_wrapper_CCA'

    def setup(self):
        self.entries_names = ['task_CCA']


class TargetMulticolorSwitcherCCABalanced(TargetMulticolorSwitcher):
    name = 'tmc_wrapper_CCA_balanced'

    def setup(self):
        self.entries_names = ['task_CCA_balanced']


class TargetMulticolorSwitcherMGRACCA(TargetMulticolorSwitcher):
    name = 'tmc_wrapper_MGRA_CCA'

    def setup(self):
        self.entries_names = ['task_CCA_MGRA']


class TargetMulticolorSwitcherMGRACCABalanced(TargetMulticolorSwitcher):
    name = 'tmc_wrapper_MGRA_CCA_balanced'

    def setup(self):
        self.entries_names = ['task_CCA_MGRA_balanced']


class TargetMulticolorSwitcherPhylogenetic(TargetMulticolorSwitcher):
    name = 'tmc_wrapper_phylo'

    def setup(self):
        self.entries_names = ['task_PhyloA']

################################################################################################################################
################################################################################################################################
################################################################################################################################


class CyclicIdentification(ExecutableContainer):
    name = 'cyclic_wrapper'

    def setup(self):
        self.self_loop = True

    def run(self, manager):
        if "assembly_points" not in manager.data["gos-asm"]:
            manager.data["gos-asm"]["assembly_points"] = []
        before = len(manager.data["gos-asm"]["assembly_points"])
        super(CyclicIdentification, self).run(manager=manager)
        self.do_self_loop = len(manager.data["gos-asm"]["assembly_points"]) - before > 0


class CyclicMGRACCA(CyclicIdentification):
    name = "cyclic_wrapper_MGRA_CCA"

    def setup(self):
        super(CyclicMGRACCA, self).setup()
        self.entries_names = ['task_GG_MGRA', 'tmc_wrapper_MGRA_CCA']


class CyclicMGRACCABalanced(CyclicIdentification):
    name = 'cyclic_wrapper_MGRA_CCA_balanced'

    def setup(self):
        super(CyclicMGRACCABalanced, self).setup()
        self.entries_names = ['task_GG_MGRA', 'tmc_wrapper_MGRA_CCA_balanced']
