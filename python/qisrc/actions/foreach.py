## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run the same command on each source project.
Example:
    qisrc foreach -- git reset --hard origin/mytag

Use -- to seprate qisrc arguments from the arguments of the command.
"""

import qisrc
import qisys
from qisys import ui

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("--ignore-errors", "--continue",
        action="store_true", help="continue on error")

def do(args):
    """Main entry point"""
    qiwt = qisys.worktree.open_worktree(args.worktree)
    errors = list()
    ui.info(ui.green, "Running `%s` on every project" % " ".join(args.command))
    git_projects = qisrc.git.get_git_projects(qiwt.projects)
    count = len(git_projects)
    for i, project in enumerate(git_projects, start=1):
        command = args.command[:]
        ui.info(ui.green, "*", ui.reset, "(%d/%d)" % (i, count), ui.blue, project.src)
        try:
            qisys.command.call(command, cwd=project.path)
        except qisys.command.CommandFailedException:
            if args.ignore_errors:
                errors.append(project)
                continue
            else:
                raise
    if not errors:
        return
    ui.error("Command failed on the following projects:")
    for project in errors:
        ui.info(ui.bold, " - ", project.src)
