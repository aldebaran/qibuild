## Copyright (C) 2011 Aldebaran Robotics

"""Init a new qisrc workspace """

import os
import logging
import qibuild
import qisrc

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.qiworktree.work_tree_parser(parser)
    parser.add_argument("--continue", action="store_true", dest="continue_on_error", help="continue on error")
    parser.add_argument("--rebase", action="store_true", dest="rebase", help="rebase")

def do(args):
    """Main entry point"""
    qiwt = qibuild.qiworktree_open(args.work_tree, use_env=True)
    for git_project in qiwt.git_projects.values():
        try:
            git = qisrc.git.open(git_project)
            #TODO: replace by try/except?
            if git.is_valid():
                if git.get_current_remote_url() == None:
                    LOGGER.debug("Not pulling. No remote for %s", git_project)
                    continue
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

