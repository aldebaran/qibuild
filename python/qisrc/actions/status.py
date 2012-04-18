## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List all git repositories and exit
"""

import os
import sys
import logging

import qibuild
import qisrc

LOGGER = logging.getLogger("qisrc.status")

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("--untracked-files", "-u",
        dest="untracked_files",
        action="store_true",
        help="display untracked files")
    parser.add_argument("--show-branch", "-b",
        dest="show_branch",
        action="store_true",
        help="display branch and tracking branch for each repository")

def _max_len(wt, projects):
    """ Helper function to display status """
    max_len = 0
    for p in projects:
        shortpath = os.path.relpath(p.src, wt)
        if len(shortpath) > max_len:
            max_len = len(shortpath)
    return max_len

def _add_pad(max_len, k, v):
    pad = " " * (max_len - len(k))
    return "%s%s%s" % (str(k), pad, str(v))

def _pad(szold, sznew):
    if sznew > szold:
        return ""
    return " " * (szold - sznew)


def do(args):
    """ Main method """
    qiwt = qisrc.open_worktree(args.worktree)
    gitrepo = list()
    dirty = list()
    sz = len(qiwt.git_projects)
    i = 1
    oldsz = 0
    for git_project in qiwt.git_projects:
        git = qisrc.git.open(git_project.path)
        if sys.stdout.isatty():
            src = git_project.src
            to_write = "checking (%d/%d)" % (i, sz)
            to_write += src
            to_write += _pad(oldsz, len(src))
            sys.stdout.write(to_write + "\r")
            sys.stdout.flush()
            oldsz = len(src)
            if i == sz:
                print "checking (%d/%d): done" % (i, sz), _pad(oldsz, 2)
        i = i + 1
        if git.is_valid():
            clean = git.is_clean(untracked=args.untracked_files)
            if args.show_branch or not clean:
                gitrepo.append(git_project)
            if not clean:
                dirty.append(git_project)

    LOGGER.info("Dirty projects: %d/%d", len(dirty), len(qiwt.git_projects))

    max_len = _max_len(qiwt.root, gitrepo)
    for git_project in gitrepo:
        git = qisrc.git.open(git_project.path)
        shortpath = os.path.relpath(git_project.path, qiwt.root)
        if git.is_valid():
            branch = git.get_current_branch()
            tracking = git.get_tracking_branch()
            line = _add_pad(max_len, shortpath, " : %s tracking %s" %
                (branch, tracking))
            LOGGER.info(line)
        if not git.is_clean(untracked=args.untracked_files):
            if args.untracked_files:
                (status_, out) = git.call("status", "-s", raises=False)
            else:
                (status_, out) = git.call("status", "-suno", raises=False)
            nlines = [ x[:3] + shortpath + "/" + x[3:] for x in out.splitlines() if len(x.strip()) > 0 ]
            print "\n".join(nlines)


    if not args.untracked_files:
        print
        print("Tips: use -u to show untracked files")

