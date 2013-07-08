#!/usr/bin/env python

## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Implement qibuild jar for qiMvn.
"""

import os

import qibuild
import qisys.command

from qisys import ui

def jar(jar_path, files, config=None):
    """ Search each files using qibuild find and
        add them into a jar using qibuild run
    """
    # Get project list
    build_worktree = qibuild.parsers.get_build_worktree(None)
    if config:
        build_worktree.set_active_config(config)
    projects = build_worktree.build_projects

    # Create command line
    jar_path = qisys.sh.to_native_path(jar_path)
    args = ["cvfM"]
    args += [jar_path]

    if not files:
        raise Exception("Missing arguments : Files to package")
    ui.debug("Searching for", files)
    for f in files:
        ui.info("Searching for " + f + "...")
        path = qibuild.find.find(projects, f)
        if not path:
            ui.error("Cannot find " + f + " in worktree")
            return None
        ui.debug("Found : " + path)
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        args += ["-C", dirname, basename]
        ui.debug("Added -C " + dirname + " " + f + " to command line")

    qisys.command.call(["jar"] + args, ignore_ret_code=False)
    return jar_path
