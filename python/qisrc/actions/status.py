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
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("--untracked-files", "-u", dest="untracked_files", action="store_true", help="display untracked files")
    parser.add_argument("--show-branch", "-b", dest="show_branch", action="store_true", help="display branch and tracking branch for each repository")

def _max_len(wt, names):
    """ Dump an argparser namespace to log """
    output = ""
    max_len = 0
    for k in names:
        shortpath = os.path.relpath(k, wt)
        if len(shortpath) > max_len:
            max_len = len(shortpath)
    return max_len

def _add_pad(max_len, k, v):
    pad = "".join([ " " for x in range(max_len - len(k)) ])
    return "%s%s%s" % (str(k), pad, str(v))

def do(args):
    """ Main method """
    qiwt = qibuild.worktree_open(args.work_tree)
    gitrepo = list()
    dirty = list()
    for git_project in qiwt.git_projects.values():
        git = qisrc.git.open(git_project)
        if git.is_valid():
            clean = git.is_clean(untracked=args.untracked_files)
            if args.show_branch or not clean:
                gitrepo.append(git_project)
            if not clean:
                dirty.append(git_project)

    LOGGER.info("Dirty projects: %d/%d", len(dirty), len(qiwt.git_projects))

    max_len = _max_len(qiwt.work_tree, gitrepo)
    for git_project in gitrepo:
        git = qisrc.git.open(git_project)
        shortpath = os.path.relpath(git_project, qiwt.work_tree)
        if git.is_valid():
            line = _add_pad(max_len, shortpath, " : %s tracking %s" % (git.get_current_branch(), git.get_tracking_branch()))
            LOGGER.info(line)
        if not git.is_clean(untracked=args.untracked_files):
            if args.untracked_files:
                lines = git.cmd.call_output("status", "-s")
            else:
                lines = git.cmd.call_output("status", "-suno")
            nlines = [ x[:3] + shortpath + "/" + x[3:] for x in lines if len(x.strip()) > 0 ]
            print "\n".join(nlines)


    if not args.untracked_files:
        print
        print("Tips: use -u to show untracked files")

