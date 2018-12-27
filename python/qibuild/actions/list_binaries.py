#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
List every binaries in the given worktree.
Mainly useful to auto-complete ``qibuild run``.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qibuild.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qibuild.parsers.cmake_build_parser(parser)


def do(args):
    """ Main entry point. """
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
    for binary in sorted(res):
        ui.info(binary)
