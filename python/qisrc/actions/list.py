## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the names and paths of every project, or those matching a pattern

"""

import re
import os
import sys

from qisys import ui
import qisys.parsers
import qisys.interact


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("--with-path", action="store_true",
                        help="Print the absolute path too.")
    parser.add_argument("pattern", metavar="PATTERN", nargs="?",
                        help="pattern to be matched")

def do(args):
    """ Main method """
    worktree = qisys.worktree.open_worktree(args.worktree)
    if not worktree.projects:
        on_empty_worktree(worktree)
    regex = args.pattern
    if args.pattern:
        regex = re.compile(regex)
    mess = [ui.green, "Projects in :", ui.reset, ui.bold, worktree.root]
    if args.pattern:
        mess.extend([ui.green, "matching", args.pattern])
    ui.info(*mess)
    to_remove = list()

    # Compute max len of src to align path if needed.
    max_length = max((len(x.src) for x in worktree.projects))

    for project in worktree.projects:
        if not regex or regex.search(project.src):
            src = project.src.ljust(max_length)
            mess = [ui.green, " *", ui.blue, src]
            if args.with_path:
                mess.extend([ui.yellow, "==>"])
                mess.extend([ui.fuchsia, ui.bold, project.path])
            ui.info(*mess)

def on_empty_worktree(worktree):
    mess = """The worktree in {worktree.root}
does not contain any project.

Please use:
    * `qisrc init` to fetch some sources
    * `qisrc add` to register a new project path to this worktree
"""
    ui.warning(mess.format(worktree=worktree))
    sys.exit(0)
