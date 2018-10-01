#!usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import importlib
import os
import sys

from bg.utils import recursive_dict_update

from gos_asm.algo import default_configuration
from gos_asm.manager_assembler import AssemblyManager

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, ".."))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gene order based scaffolder")
    parser.add_argument("configuration_file",
                        nargs=1,
                        help="A fully qualifying path to gos-asm configuration .py file." +
                             "File must contain a configuration entry which is described with dictionary python structure")
    arguments = parser.parse_args()
    manager = None
    config = {}
    try:
        module_path, file_name = os.path.split(arguments.configuration_file[0])
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        module_name = file_name[:file_name.rfind(".")]
        module = importlib.import_module(module_name)
        config = module.configuration
    except Exception as exc:
        print(exc)
        print("Error importing configurations")
        exit(1)
    manager_config = recursive_dict_update(default_configuration.configuration, config)
    manager = AssemblyManager(config=manager_config)
    manager.run()

