## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run the same command on each buildable project.

Use -- to separate qibuild arguments from the arguments of the command.
For instance
  qibuild --ignore-errors -- ls -l
"""

import qisys.log

import qibuild
import qibuild.project


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("--continue", "--ignore-errors", dest="ignore_errors",
                        action="store_true", help="continue on error")

def do(args):
    """Main entry point"""
    qiwt = qisys.worktree.open_worktree(args.worktree)
    logger = qisys.log.get_logger(__name__)
    for project in qibuild.project.build_projects(qiwt):
        logger.info("Running `%s` for %s", " ".join(args.command), project.src)
        try:
            qisys.command.call(args.command, cwd=project.path)
        except qisys.command.CommandFailedException, err:
            if args.ignore_errors:
                logger.error(str(err))
                continue
            else:
                raise

