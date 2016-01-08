# -*- coding: utf-8 -*-
from gos.executable_containers import ExecutableContainer

def string_representation_of_multicolor(multicolor):
    return ", ".join(color.name for color in sorted(multicolor.colors))


class TargetMulticolorSwitcher(ExecutableContainer):
    name = 'tmc_wrapper'

    def setup(self):
        self.entries_names = ['task_CCA']

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
            super().run(manager=manager)

class TargetMulticolorSwitcherMGRA(ExecutableContainer):
    name = 'tmc_wrapper_MGRA'

    def setup(self):
        self.entries_names = ['task_CCA_MGRA']

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
            super().run(manager=manager)
