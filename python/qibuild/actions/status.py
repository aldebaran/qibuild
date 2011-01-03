##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

"""display the status of projects

List all buildable projects found. For each project, display the list of build directory.
"""

import os
import sys
import glob
import time
import datetime
import logging
import qibuild
import qitools

LOGGER = logging.getLogger(__name__)

def usage():
    "Specific usage"
    return """status [--all,-a] [projects..]"""

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
            pad = "".join([ " " for x in range(max_len - len(bdir)) ])
            print " %s%s: (%s)" % (os.path.basename(bdir), pad, todisplay)

def do(args):
    """Main entry point"""
    qiwt = qitools.qiworktree.open(args.work_tree, use_env=True)
    max_len = 0
    for pname, ppath in qiwt.buildable_projects.iteritems():
        if len(pname) > max_len:
            max_len = len(pname)

    for pname, ppath in qiwt.buildable_projects.iteritems():
        pad = "".join([ " " for x in range(max_len - len(pname)) ])
        LOGGER.info(os.path.relpath(ppath, qiwt.work_tree))
        #print "%s%s [%s]" %(pname, pad, os.path.relpath(ppath, qiwt.work_tree))
        list_build_dir(ppath)

if __name__ == "__main__" :
    qitools.cmdparse.sub_command_main(sys.modules[__name__])

