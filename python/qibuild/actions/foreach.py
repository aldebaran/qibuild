## Copyright (C) 2011 Aldebaran Robotics

"""Run the same command on each buildable project.

Use -- to separate qibuild arguments from the arguments of the command.
For instance
  qibuild --ignore-errors -- ls -l
"""

import sys
import logging
import qitools


def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)
    parser.add_argument("command", metavar="COMMAND", nargs="+")
    parser.add_argument("--ignore-errors", action="store_true", help="continue on error")

def do(args):
    """Main entry point"""
    qiwt = qitools.qiworktree_open(args.work_tree, use_env=True)
    logger = logging.getLogger(__name__)
    for pname, ppath in qiwt.buildable_projects.iteritems():
        logger.info("Running `%s` for %s", " ".join(args.command), pname)
        try:
            qitools.command.check_call(args.command, cwd=ppath)
        except qitools.command.CommandFailedException, err:
            if args.ignore_errors:
                logger.error(str(err))
                continue
            else:
                raise

if __name__ == "__main__" :
    qitools.cmdparse.sub_command_main(sys.modules[__name__])

