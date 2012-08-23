## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the names and paths of every project, or those matching a pattern

"""

import re
import os
import sys

from qibuild import ui
import qisrc
import qibuild
import qibuild.interact


def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("pattern", metavar="PATTERN", nargs="?",
                        help="pattern to be matched")

def do(args):
    """ Main method """
    worktree = qisrc.open_worktree(args.worktree)
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
    for project in worktree.projects:
        if not regex or regex.search(project.src):
           ui.info(ui.green, " *", ui.blue, project.src)
           if not os.path.exists(project.path):
               to_remove.append(project.src)
    if not to_remove:
        return
    mess = "The following projects:\n"
    for rm in to_remove:
        mess += " * " + rm + "\n"
    mess += "are registered in the worktree, but their paths no longer exists"
    ui.warning(mess)
    answer = qibuild.interact.ask_yes_no("Do you want to remove them", default=True)
    if not answer:
        return
    for rm in to_remove:
        ui.info(ui.green, "Removing", rm)
        worktree.remove_project(rm)

def on_empty_worktree(worktree):
    mess = """The worktree in {worktree.root}
does not contain any project.

Please use:
    * `qisrc init` to fetch some sources
    * `qisrc add` to register a new project path to this worktree
"""
    ui.warning(mess.format(worktree=worktree))
    sys.exit(0)
