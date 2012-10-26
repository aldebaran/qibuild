## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Display the status of each project
"""

import os
import glob
import time
import datetime
import qisys.log

import qisrc
import qibuild

LOGGER = qisys.log.get_logger(__name__)

def usage():
    "Specific usage"
    return """status [--all, -a] [projects...]"""

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)

def list_build_dir(path):
    """ list all buildable directory """
    bdirs = glob.glob(os.path.join(path, "build-*"))
    max_len = 0
    for bdir in bdirs:
        if len(bdir) > max_len:
            max_len = len(bdir)

    for bdir in bdirs:
        if os.path.isdir(bdir):
            ctim = time.time()
            ftim = os.path.getmtime(bdir)
            delta = ctim - ftim
            ddelta = datetime.timedelta(seconds = delta)
            todisplay = ""
            if ddelta.days > 0:
                todisplay = "%d days, %d hours" % (ddelta.days, ddelta.seconds / 3600)
            elif ddelta.seconds > 3600:
                todisplay = "%d hours" % (ddelta.seconds / 3600)
            else:
                todisplay = "%d minutes" % (ddelta.seconds / 60)
            pad = " " * (max_len - len(bdir))
            print " %s%s: (%s)" % (os.path.basename(bdir), pad, todisplay)

def do(args):
    """Main entry point"""
    qiwt = qisys.worktree.open_worktree(args.worktree)
    for project in qiwt.buildable_projects:
        LOGGER.info("%s", project.src)
        list_build_dir(project.path)
