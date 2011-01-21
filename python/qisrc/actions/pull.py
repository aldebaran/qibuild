##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

"""Init a new qisrc workspace """

import os
import logging
import qitools
import qisrc

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)
    parser.add_argument("--continue", action="store_true", dest="continue_on_error", help="continue on error")
    parser.add_argument("--rebase", action="store_true", dest="rebase", help="rebase")

def do(args):
    """Main entry point"""
    qiwt = qitools.qiworktree.open(args.work_tree, use_env=True)
    for git_project in qiwt.git_projects.values():
        try:
            git = qisrc.git.open(git_project)
            #TODO: replace by try/except?
            if git.is_valid():
                LOGGER.info("Pull %s", git_project)
                if args.rebase:
                    git.pull('--rebase')
                else:
                    git.pull()
        except Exception, e:
            if (args.continue_on_error):
                continue
            else:
                raise

