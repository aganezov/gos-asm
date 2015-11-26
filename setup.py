#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='gos-asm',
      version='0.0.0-a',
      description='Multi-genome gene order based assembler',
      install_requires=list(map(lambda entry: entry.strip(), open("requirements.txt", "rt").readlines())),
      author='Sergey Aganezov',
      author_email='aganezov@gwu.edu',
      license="LGPLv3",
      keywords=["breakpoint graph", "data structures", "python", "scaffolding", "gene order", "assembly", "genome"],
      url='https://github.com/aganezov/gos-asm',
      packages=['gos_asm', 'tests'],
      test_suite="tests",
      classifiers=[
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
      ]
      )
