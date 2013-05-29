## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Run a package found with qibuild find

"""

import sys

from qisys import ui
import qibuild.find
import qibuild.parsers
import qisys.parsers
import qisys.command

def run(projects, binary, bin_args):
    """ Find binary in worktree and
        exec it with given arguments.
    """
    paths = list()
    for proj in projects:
        paths += [proj.sdk_directory]
    bin_path = qibuild.find.find(paths, binary)
    if not bin_path:
        bin_path = qisys.command.find_program(binary)
    if not bin_path:
        raise Exception("Cannot find " + binary + " binary")
    try:
        retcode = qisys.command.call([bin_path] + bin_args, ignore_ret_code=False)
    except qisys.command.CommandFailedException as e:
        retcode = e.returncode
    return retcode
