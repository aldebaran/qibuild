## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run git grep on every project

Options are the same as in git grep, e.g.:

  qisrc grep -- -niC2 foo

"""

import sys
import qibuild.log

import qisrc
import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("git_grep_opts", metavar="-- git grep options", nargs="*",
                        help="git grep options preceeded with -- to escape the leading '-'")
    parser.add_argument("pattern", metavar="PATTERN",
                        help="pattern to be matched")

def do(args):
    """ Main entry point """
    qiwt = qisrc.open_worktree(args.worktree)
    git_grep_opts = args.git_grep_opts
    git_grep_opts.append(args.pattern)
    logger = qibuild.log.get_logger(__name__)
    retcode = 0
    for project in qiwt.git_projects:
        qibuild.ui.info(qibuild.ui.green,
                        "Looking in", project.src, "...",
                        qibuild.ui.reset)
        git = qisrc.git.Git(project.path)
        (status, out) = git.call("grep", *git_grep_opts, raises=False)
        print out
        if status != 0:
            retcode = 1
    sys.exit(retcode)
