## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run the same command on each source project.
Example:
    qisrc foreach -- git reset --hard origin/mytag

Use -- to seprate qisrc arguments from the arguments of the command.
"""

import qisys.actions
import qisys.parsers
import qisrc.parsers

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisrc.parsers.groups_parser(parser)
    parser.add_argument("--git", action="store_true", dest="git_only",
        help="consider only the git projects")
    parser.add_argument("--all", action="store_false", dest="git_only",
        help="consider all the projects")
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("-c", "--ignore-errors", "--continue",
        action="store_true", help="continue on error")
    parser.set_defaults(git_only=True)

def do(args):
    """Main entry point"""
    if args.git_only:
        git_worktree = qisrc.parsers.get_git_worktree(args)
        projects = git_worktree.get_git_projects(groups=args.groups)
    else:
        worktree = qisys.parsers.get_worktree(args)
        projects = worktree.projects

    qisys.actions.foreach(projects, args.command,
                          ignore_errors=args.ignore_errors)
