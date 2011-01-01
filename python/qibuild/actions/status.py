##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""display the status of projects

List all buildable projects found. For each project, display the list of build directory.
"""

import os
import sys
import glob
import logging
import qibuild

def usage():
    "Specific usage"
    return """status [--all,-a] [projects..]"""

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.shell.toc_parser(parser)

def list_build_dir(project):
    """ list all buildable directory """
    bdirs = glob.glob(os.path.join(project.directory, "build-*"))
    for bdir in bdirs:
        if os.path.isdir(bdir):
            print " ", os.path.basename(bdir)

def do(args):
    """Main entry point"""
    toc = qibuild.toc.toc_open(args.work_tree, use_env=True)
    logger = logging.getLogger(__name__)
    max_len = 0
    for project in toc.buildable_projects.values():
        if len(project.name) > max_len:
            max_len = len(project.name)

    for project in toc.buildable_projects.values():
        pad = "".join([ " " for x in range(max_len - len(project.name)) ])
        print "%s%s [%s]" %(project.name, pad, os.path.relpath(project.directory, toc.work_tree))
        list_build_dir(project)

if __name__ == "__main__" :
    qibuild.shell.sub_command_main(sys.modules[__name__])

