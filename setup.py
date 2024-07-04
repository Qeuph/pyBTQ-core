#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This file was generated with PyScaffold 3.0.2.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: http://pyscaffold.org/
"""

import sys
from setuptools import setup
import versioneer

# Add here console scripts and other entry points in ini-style format
entry_points = """
[console_scripts]
    start_btq = btq.main:main
    btq_start = btq.main:main
    btq = btq.cli:main
    btq_grpc_proxy = btq.grpcProxy:main
    btq_measure = btq.measure:main
    btq_walletd = btq.daemon.walletd:main
    btq_generate_genesis = btq.tools.generate_genesis:main
"""


def setup_package():
    needs_sphinx = {'build_sphinx', 'upload_docs'}.intersection(sys.argv)
    sphinx = ['sphinx'] if needs_sphinx else []
    setup(setup_requires=['pyscaffold>=3.0a0,<3.1a0'] + sphinx,
          entry_points=entry_points,
          version=versioneer.get_version(),
          cmdclass=versioneer.get_cmdclass(),
          use_pyscaffold=True)


if __name__ == "__main__":
    setup_package()
