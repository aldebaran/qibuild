# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Run a package found with qibuild find

"""
import os

from qisys import ui
import qisys.command
import qisys.interact
import qisys.parsers
import qibuild.find
import qibuild.parsers


def run(projects, binary, bin_args, env=None, exec_=True):
    """ Find binary in worktree and
        exec it with given arguments.
    """
    paths = list()
    for proj in projects:
        paths += [proj.sdk_directory]
    full_path = qisys.sh.to_native_path(binary)
    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
        bin_path = full_path
    else:
        bin_path = None
        candidates = qibuild.find.find_bin(paths, binary, expect_one=False)
        if len(candidates) == 1:
            bin_path = candidates[0]
        if len(candidates) > 1:
            bin_path = qisys.interact.ask_choice(candidates,
                                                 "Please select a binary to run")
    if not bin_path:
        bin_path = qisys.command.find_program(binary)
    if not bin_path:
        raise Exception("Cannot find " + binary + " binary")
    cmd = [bin_path] + bin_args
    if exec_:
        ui.debug("exec", cmd)
        os.execve(bin_path, cmd, env)
    else:
        qisys.command.call(cmd, env=env)
