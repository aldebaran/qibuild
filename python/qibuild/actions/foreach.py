## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run the same command on each buildable project.

Use -- to separate qibuild arguments from the arguments of the command.
For instance
  qibuild --ignore-errors -- ls -l
"""

import logging
import qibuild


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("--ignore-errors", action="store_true", help="continue on error")

def do(args):
    """Main entry point"""
    qiwt = qibuild.open_worktree(args.worktree)
    logger = logging.getLogger(__name__)
    for project in qiwt.buildable_projects:
        logger.info("Running `%s` for %s", " ".join(args.command), project.name)
        try:
            qibuild.command.call(args.command, cwd=project.src)
        except qibuild.command.CommandFailedException, err:
            if args.ignore_errors:
                logger.error(str(err))
                continue
            else:
                raise

