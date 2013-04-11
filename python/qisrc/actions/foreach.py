## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
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
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser, positional=False)
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("--ignore-errors", "--continue",
        action="store_true", help="continue on error")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")

def do(args):
    """Main entry point."""
    qiwt = qisys.worktree.open_worktree(args.worktree)
    errors = list()

    # Found on which projects launch the command
    git_projects = qisrc.cmdparse.projects_from_args(args, qiwt)
    git_projects = qisrc.git.get_git_projects(git_projects)
    nbr_git_projects = len(git_projects)

    # Compute the total of git projects
    nbr_all_git_projects = len(qisrc.git.get_git_projects(qiwt.projects))

    if not git_projects:
        ui.error("There is no Git projects here.")
        return

    # Print the command and the projects
    if args.dry_run:
        ui.info(ui.green, "Would run", end="")
    else:
        ui.info(ui.green, "Running", end="")
    ui.info(ui.green, "`%s` on" % " ".join(args.command), end="")
    if nbr_git_projects == nbr_all_git_projects:
        ui.info(ui.green, "all", end="")
    else:
        ui.info(ui.green, "%i" % nbr_git_projects, end="")
    ui.info(ui.green, "projects")

    count = len(git_projects)
    for i, project in enumerate(git_projects, start=1):
        command = args.command[:]
        ui.info(ui.green, "*", ui.reset, "(%d/%d)" % (i, count), ui.blue, project.src)
        if args.dry_run:
            continue
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
