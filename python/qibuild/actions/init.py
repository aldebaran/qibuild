"""Init a new toc workspace """

import os
import qibuild
import qitools.cmdparse

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    group = parser.add_argument_group("build configuration settings")
    group.add_argument("--build-config-name", metavar="BUILD_CONFIGS",
        help="list of build configurations names")
    group.add_argument("--build-config-flags", metavar="BUILD_CONFIG_FLAGS",
        nargs="+")
    group.add_argument("--path", metavar="PATH",
        help="to be added to PATH environment variable")
    group.add_argument("--bat-file", help="a .bat file to be sourced")
    group.add_argument("--cmake-generator", help="name of the cmake generator to use")

def do(args):
    """Main entry point"""
    work_tree = qitools.qiworktree.worktree_from_args(args)
    qibuild.toc.create(work_tree, args)

if __name__ == "__main__" :
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])
