##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""Init a new qisrc workspace """

import os
import qibuild
import qisrc


def configure_parser(parser):
    """Configure parser for this action """
    qitools.argparsecommand.toc_parser(parser)
    parser.add_argument("--continue", action="store_true", dest="continue_on_error", help="continue on error")

def do(args):
    """Main entry point"""
    qis = qisrc.open(args.work_tree, use_env=True)
    for git_project in qis.git_projects:
        try:
            git = qisrc.git.open(git_project)
            #TODO: replace by try/except?
            if git.is_valid():
                print "pull:", git_project
                git.pull()
        except Exception, e:
            if (args.continue_on_error):
                continue
            else:
                raise

if __name__ == "__main__" :
    import sys
    qitools.argparsecommand.sub_command_main(sys.modules[__name__])
