## Copyright (C) 2011 Aldebaran Robotics

""" Run git pull on every git projects of a worktree

"""

import os
import logging
import qibuild
import qisrc

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("--continue", action="store_true", dest="continue_on_error", help="continue on error")
    parser.add_argument("--stop-on-error", action="store_false", dest="continue_on_error", help="continue on error")
    parser.add_argument("--rebase", action="store_true", dest="rebase", help="rebase")
    parser.set_defaults(continue_on_error=True)

def do(args):
    """Main entry point"""
    fail = list()
    qiwt = qibuild.worktree_open(args.work_tree)
    for git_project in qiwt.git_projects.values():
        git = qisrc.git.open(git_project)
        LOGGER.info("Pull %s", git_project)
        if args.rebase:
            out = git.cmd.call_output("pull", "--rebase", rawout=True)
        else:
            out = git.cmd.call_output("pull", rawout=True)
        out = git.cmd.call_output("pull", rawout=True)
        if out[0] == 0:
            print out[1][0],
            print out[1][1],
        else:
            fail.append((git_project, out))
            if not args.continue_on_error:
                raise Exception("\n%s%s" % (out[1][0], out[1][1]))

    if len(fail) > 0:
        print ""
        LOGGER.info("=====================")
        LOGGER.info("Projects that failed:")
        print "\n".join(x[0] for x in fail)
        LOGGER.info("=====================")
        print ""
        LOGGER.info("details:")

    for f in fail:
        LOGGER.error(f[0])
        print f[1][1][0],
        print f[1][1][1],
