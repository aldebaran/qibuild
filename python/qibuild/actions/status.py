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
import logging
import qibuild
import qitools

def usage():
    "Specific usage"
    return """status [--all,-a] [projects..]"""

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)

def list_build_dir(path):
    """ list all buildable directory """
    bdirs = glob.glob(os.path.join(path, "build-*"))
    for bdir in bdirs:
        if os.path.isdir(bdir):
            print " ", os.path.basename(bdir)

def do(args):
    """Main entry point"""
    qiwt = qitools.qiworktree.open(args.work_tree, use_env=True)
    logger = logging.getLogger(__name__)
    max_len = 0
    for pname, ppath in qiwt.buildable_projects.iteritems():
        if len(pname) > max_len:
            max_len = len(pname)

    for pname, ppath in qiwt.buildable_projects.iteritems():
        pad = "".join([ " " for x in range(max_len - len(pname)) ])
        print "%s%s [%s]" %(pname, pad, os.path.relpath(ppath, qiwt.work_tree))
        list_build_dir(ppath)

if __name__ == "__main__" :
    qitools.cmdparse.sub_command_main(sys.modules[__name__])

