## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the known profiles of the given worktree """

from qisys import ui
import qisys.parsers
import qibuild.parsers

def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)

def do(args):
    """" Main entry point """
    build_worktree = qibuild.parsers.get_build_worktree(args, verbose=False)
    profiles = build_worktree.get_known_profiles()
    profile_names = profiles.keys()
    profile_names.sort()
    for profile_name in profile_names:
        profile = profiles[profile_name]
        ui.info(" * ", ui.blue, profile_name)
        max_len = max(len(x[0])for x in profile.cmake_flags)
        for (flag_name, flag_value) in profile.cmake_flags:
            ui.info(" " * 4, flag_name.ljust(max_len + 2), ":", flag_value)
        ui.info()
