"""Init a new toc workspace """

import os
import qibuild
import qitools.cmdparse

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)

def do(args):
    """Main entry point"""
    work_tree = qitools.qiworktree.worktree_from_args(args)
    qibuild.toc.create(work_tree, args)

if __name__ == "__main__" :
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])
