## Copyright (C) 2011 Aldebaran Robotics

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
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("--ignore-errors", "--continue",
        action="store_true", help="continue on error")

def do(args):
    """Main entry point"""
    qiwt = qibuild.worktree_open(args.work_tree)
    logger = logging.getLogger(__name__)
    for pname, ppath in qiwt.git_projects.iteritems():
        logger.info("Running `%s` for %s", " ".join(args.command), pname)
        try:
            qibuild.command.call(args.command, cwd=ppath)
        except qibuild.command.CommandFailedException, err:
            if args.ignore_errors:
                continue
            else:
                raise

