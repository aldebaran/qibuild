## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Implement qibuild jar for qiMvn.
"""

import os

import qibuild
import qisys.command

from qisys import ui

def jar(jar_path, files, paths):
    """ Search each files using qibuild find and
        add them into a jar using qisys
    """

    # Create command line
    jar_path = qisys.sh.to_native_path(jar_path)
    args = ["cvfM"]
    args += [jar_path]

    if not files:
        raise Exception("Missing arguments : Files to package")
    for wanted_file in files:
        ui.info("Searching for " + wanted_file + "...")
        path = qibuild.find.find(paths, wanted_file, expect_one=False)[0]
        if not path:
            ui.error("Cannot find " + wanted_file + " in worktree")
            return None
        ui.debug("Found : " + path)
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        args += ["-C", dirname, basename]
        ui.debug("Added -C " + dirname + " " + wanted_file + " to command line")

    qisys.command.call(["jar"] + args, ignore_ret_code=False)
    return jar_path
