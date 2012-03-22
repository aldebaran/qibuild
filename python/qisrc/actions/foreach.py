## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run the same command on each source project.
Example:
    qisrc foreach -- git reset --hard origin/mytag

Use -- to seprate qisrc arguments from the arguments of the command.
"""

import sys
import logging
import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("--ignore-errors", "--continue",
        action="store_true", help="continue on error")

def do(args):
    """Main entry point"""
    qiwt = qibuild.open_worktree(args.worktree)
    logger = logging.getLogger(__name__)
    for project in qiwt.git_projects:
        logger.info("Running `%s` for %s", " ".join(args.command), project.name)
        try:
            qibuild.command.call(args.command, cwd=project.src)
        except qibuild.command.CommandFailedException:
            if args.ignore_errors:
                continue
            else:
                raise

