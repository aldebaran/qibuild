##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

""" clean build directories

By default all build directories for all project are removed.
You can specify a list of build directory name to cleanup.
"""

import os
import glob
import logging
import qibuild
import qitools.argparsecommand

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("--force", "-f", dest="force", action="store_true", help="force the cleanup")
    parser.add_argument("build_directory", nargs="*", help="build directory to cleanup")


def cleanup(project, bdirs, work_tree, doit=False):
    """ list all buildable directory """
    if not len(bdirs):
        bdirs = glob.glob(os.path.join(project.directory, "build-*"))
    else:
        bdirs = [ os.path.join(project.directory, x) for x in bdirs ]
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
    toc      = qibuild.toc.open(args.work_tree, use_env=True)

    if args.force:
        print "removing:"
    else:
        print "Build directory that will be removed (use -f to apply):"
    for project in toc.buildable_projects.values():
        cleanup(project, args.build_directory, toc.work_tree, args.force)

if __name__ == "__main__":
    import sys
    qitools.argparsecommand.sub_command_main(sys.modules[__name__])


