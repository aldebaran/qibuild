## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List every all the binaries in the given worktree.

"""
# Mainly useful to auto-complete ``qibuild run``

import os

from qisys import ui
import qibuild.parsers

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.cmake_build_parser(parser)

def do(args):
    """ Main entry point """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    sdk_dirs = [x.sdk_directory for x in build_worktree.build_projects]
    bin_dirs = [os.path.join(x, "bin") for x in sdk_dirs]
    res = list()
    for bin_dir in bin_dirs:
        if os.path.exists(bin_dir):
            binaries = os.listdir(bin_dir)
        else:
            binaries = list()
        if os.name == 'nt':
            binaries = [x for x in binaries if x.endswith(".exe")]
            binaries = [x.replace("_d.exe", "") for x in binaries]
            binaries = [x.replace(".exe", "") for x in binaries]
        res.extend(binaries)

    res.sort()
    for binary in res:
        ui.info(binary)
