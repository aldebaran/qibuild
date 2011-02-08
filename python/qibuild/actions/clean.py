## Copyright (C) 2011 Aldebaran Robotics

""" Clean build directories.

By default all build directories for all projects are removed.
You can specify a list of build directory names to cleanup.
"""

import os
import glob
import logging
import qibuild
import qitools

def configure_parser(parser):
    """Configure parser for this action"""
    qitools.qiworktree.work_tree_parser(parser)
    parser.add_argument("--force", "-f", dest="force", action="store_true", help="force the cleanup")
    parser.add_argument("build_directory", nargs="*", help="build directory to cleanup")

def cleanup(path, bdirs, work_tree, doit=False):
    """ list all buildable directory """
    if not len(bdirs):
        bdirs = glob.glob(os.path.join(path, "build-*"))
    else:
        bdirs = [ os.path.join(path, x) for x in bdirs ]
    for bdir in bdirs:
        if os.path.isdir(bdir):
            if doit:
                print " ", os.path.relpath(bdir, work_tree)
                qitools.sh.rm(bdir)
            else:
                print " ", os.path.relpath(bdir, work_tree)
    pass

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    qiwt     = qitools.qiworktree_open(args.work_tree, use_env=True)

    if args.force:
        print "removing:"
    else:
        print "Build directory that will be removed (use -f to apply):"
    for project in qiwt.buildable_projects.values():
        cleanup(project, args.build_directory, qiwt.work_tree, args.force)

if __name__ == "__main__":
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])


