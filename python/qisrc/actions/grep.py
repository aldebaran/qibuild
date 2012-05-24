## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run git grep on every project

Options are the same as in git grep

"""

import sys
import logging

import qisrc
import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("git_grep_opts", metavar="git grep options", nargs="+")


def do(args):
    """ Main entry point """
    qiwt = qisrc.open_worktree(args.worktree)
    git_grep_opts = args.git_grep_opts
    logger = logging.getLogger(__name__)
    retcode = 0
    for project in qiwt.git_projects:
        print "Looking in", project.src, "..."
        git = qisrc.git.Git(project.path)
        (status, out) = git.call("grep", *git_grep_opts, raises=False)
        print out
        if status != 0:
            retcode = 1
    sys.exit(retcode)
