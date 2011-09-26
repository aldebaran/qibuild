## Copyright (C) 2011 Aldebaran Robotics

""" List all git repositories and exit
"""

import os
import logging

import qibuild
import qisrc

LOGGER = logging.getLogger("qisrc.status")

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.qiworktree.work_tree_parser(parser)
    parser.add_argument("--untracked-files", "-u", dest="untracked_files", action="store_true", help="display untracked files")
    parser.add_argument("--show-branch", "-b", dest="show_branch", action="store_true", help="display branch and tracking branch for each repository")

def do(args):
    """ Main method """
    qiwt = qibuild.qiworktree_open(args.work_tree)
    dirty = list()
    for git_project in qiwt.git_projects.values():
        git = qisrc.git.open(git_project)
        if git.is_valid() and not git.is_clean(untracked=args.untracked_files):
            dirty.append(git_project)

    LOGGER.info("Dirty projects: %d/%d", len(dirty), len(qiwt.git_projects))
    #we want to show all project
    if args.show_branch:
        dirty = qiwt.git_projects.values()

    for git_project in dirty:
        git = qisrc.git.open(git_project)
        if git.is_valid() and not git.is_clean(untracked=args.untracked_files):
            shortpath = os.path.relpath(git_project, qiwt.work_tree)
            LOGGER.info("%s : %s tracking %s", shortpath, git.get_current_branch(), git.get_tracking_branch())
            if args.untracked_files:
                lines = git.cmd.call_output("status", "-s")
            else:
                lines = git.cmd.call_output("status", "-suno")

            nlines = [ x[:3] + shortpath + "/" + x[3:] for x in lines if len(x.strip()) > 0 ]
            print "\n".join(nlines)
        elif git.is_valid():
            shortpath = os.path.relpath(git_project, qiwt.work_tree)
            LOGGER.info("%s : %s tracking %s", shortpath, git.get_current_branch(), git.get_tracking_branch())


    if not args.untracked_files:
        print
        print("Tips: use -u to show untracked files")

