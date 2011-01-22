##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

""" list all git repositories and exit
"""

import os
import logging

import qitools
import qisrc

LOGGER = logging.getLogger("qisrc.status")

def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)
    parser.add_argument("--untracked-files", "-u", dest="untracked_files", action="store_true", help="display untracked files")
    # qitools.cmdparse.action_parser(parser)
    # parser.add_argument("toolchain", action="store", help="the toolchain name")
    # parser.add_argument("feed", nargs='?', action="store", help="an url to a toolchain feed")

def do(args):
    """ Main method """
    qiwt = qitools.qiworktree_open(args.work_tree, use_env=True)
    dirty = list()
    for git_project in qiwt.git_projects.values():
        git = qisrc.git.open(git_project)
        if git.is_valid() and not git.is_clean(untracked=args.untracked_files):
            dirty.append(git_project)

    LOGGER.info("Dirty projects: %d/%d", len(dirty), len(qiwt.git_projects))
    for git_project in dirty:
        git = qisrc.git.open(git_project)
        if git.is_valid() and not git.is_clean(untracked=args.untracked_files):
            shortpath = os.path.relpath(git_project, qiwt.work_tree)
            #print "[ %s ]" % shortpath
            print ""
            LOGGER.info("%s : %s tracking %s", shortpath, git.get_current_branch(), git.get_tracking_branch())
            if args.untracked_files:
                lines = git.cmd.call_output("status", "-s")
            else:
                lines = git.cmd.call_output("status", "-suno")

            nlines = [ x[:3] + shortpath + "/" + x[3:] for x in lines if len(x.strip()) > 0 ]
            print "\n".join(nlines)

    if not args.untracked_files:
        print
        print("Tips: use -u to show untracked files")

if __name__ == "__main__" :
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])
