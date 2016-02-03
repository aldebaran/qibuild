## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run the same command on each qiproject.

Example:
    qisys foreach -- bash $(pwd)/fix-qiproject.sh

Use -- to separate qisys arguments from the arguments of the command.
"""

import qisys
import qisys.parsers
import qisys.actions

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("-c", "--ignore-errors", "--continue",
        action="store_true", help="continue on error")
    parser.add_argument("command", metavar="COMMAND", nargs="+")

def do(args):
    """Main entry point"""
    worktree = qisys.parsers.get_worktree(args)
    projects = worktree.projects

    qisys.foreach(projects, args.command,
                            ignore_errors=args.ignore_errors)
