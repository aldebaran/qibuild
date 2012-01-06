## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Quick rewrite of qibuild.command

(different purposes)

"""

import sys
import os
import subprocess

def call(cmd, cwd=None, env=None):
    """ Execute a command, printing only the warnings
    and the errors

    """
    if not os.environ.get("QI_BUILD_FARM"):
        subprocess.check_call(cmd, cwd=cwd, env=env)
        return

    process = subprocess.Popen(cmd, cwd=cwd, env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    while process.poll() is None:
        out = process.stdout.readline()
        if "warn" in out.lower() or "err" in out.lower():
            sys.stdout.write(out)
        sys.stdout.flush()
    retcode = process.returncode
    if retcode != 0:
        mess  = "Command failed\n"
        mess += "cmd: %s\n" % cmd
        mess += "cwd: %s\n" % cwd
        mess += "retcode: %s\n" % retcode
        raise Exception(mess)


