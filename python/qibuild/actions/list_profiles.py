#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" List the known profiles of the given worktree. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.parsers
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.worktree_parser(parser)


def do(args):
    """" Main entry point. """
    build_worktree = qibuild.parsers.get_build_worktree(args, verbose=False)
    profiles = build_worktree.get_known_profiles()
    profile_names = sorted(profiles.keys())
    for profile_name in profile_names:
        profile = profiles[profile_name]
        ui.info(" * ", ui.blue, profile_name)
        max_len = max(len(x[0])for x in profile.cmake_flags)
        for (flag_name, flag_value) in profile.cmake_flags:
            ui.info(" " * 4, flag_name.ljust(max_len + 2), ":", flag_value)
        ui.info()
