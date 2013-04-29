## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Run a package found with qibuild find

"""


import qimvn.find
import qisys.parsers
import qisys.command

def run(projects, binary, bin_args=list()):
    """ Find binary in worktree and
        exec it with given arguments.
    """
    bin_path = qimvn.find.find(projects, binary)
    command = ["java", "-jar", bin_path]
    if not bin_path:
        raise Exception("Cannot find " + binary + " binary")
    try:
        retcode = qisys.command.call(command + bin_args, ignore_ret_code=False)
    except qisys.command.CommandFailedException as exception:
        retcode = exception.returncode
    return retcode
