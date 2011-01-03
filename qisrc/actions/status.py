##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

""" list all git repositories and exit
"""

import os
import logging

import qibuild
import qisrc

LOGGER = logging.getLogger("qisrc.status")

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.shell.toc_parser(parser)
    # qibuild.shell.action_parser(parser)
    # parser.add_argument("toolchain", action="store", help="the toolchain name")
    # parser.add_argument("feed", nargs='?', action="store", help="an url to a toolchain feed")

def do(args):
    """ Main method """
    qis = qisrc.open(args.work_tree, use_env=True)
    dirty = list()
    for git_project in qis.git_projects:
        git = qisrc.git.open(git_project)
        if git.is_valid() and not git.is_clean():
            dirty.append(git_project)

    LOGGER.info("Dirty projects: %d/%d", len(dirty), len(qis.git_projects))
    for git_project in dirty:
        git = qisrc.git.open(git_project)
        if git.is_valid() and not git.is_clean():
            shortpath = os.path.relpath(git_project, qis.work_tree)
            #print "[ %s ]" % shortpath
            print ""
            LOGGER.info("%s : %s tracking %s", shortpath, git.get_current_branch(), git.get_tracking_branch())
            lines = git.cmd.call_output("status", "-s")
            nlines = [ x[:3] + shortpath + "/" + x[3:] for x in lines if len(x.strip()) > 0 ]
            print "\n".join(nlines)
            #git.status("-s", "-uno")

if __name__ == "__main__" :
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])
