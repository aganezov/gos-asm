#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='gos-asm',
      version='0.10',
      description='Multi-genome gene order based scaffold assembler',
      install_requires=["gos", "bg", "enum-compat", "networkx"],
      author='Sergey Aganezov',
      author_email='aganezov@cs.jhu.edu',
      license="MIT",
      scripts=["gos_asm/gos-asm.py"],
      keywords=["breakpoint graph", "data structures", "python", "scaffolding", "gene order", "assembly", "genome"],
      url='https://github.com/aganezov/gos-asm',
      packages=['gos_asm',
                'gos_asm.algo', 'gos_asm.algo.data_structures', 'gos_asm.algo.executable_containers', 'gos_asm.algo.shared', 'gos_asm.algo.tasks',
                'gos_asm.algo.tasks.asm', 'gos_asm.algo.tasks.io', 'gos_asm.algo.tasks.mgra',
                'gos_asm.examples',
                ],
      include_package_data=True,
      classifiers=[
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License",
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5'
      ]
      )
