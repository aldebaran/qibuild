## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Clean build directories.

By default all build directories for all projects are removed.
You can specify a list of build directory names to cleanup.
"""

import os
import glob
import logging
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("--force", "-f", dest="force", action="store_true", help="force the cleanup")
    parser.add_argument("build_directory", nargs="*", help="build directory to cleanup")

def cleanup(path, bdirs, worktree, doit=False):
    """ list all buildable directory """
    if not len(bdirs):
        bdirs = glob.glob(os.path.join(path, "build-*"))
    else:
        bdirs = [ os.path.join(path, x) for x in bdirs ]
    for bdir in bdirs:
        if os.path.isdir(bdir):
            if doit:
                print " ", os.path.relpath(bdir, worktree)
                qibuild.sh.rm(bdir)

def list_build_folder(path, bdirs, worktree):
    """ list all buildable directory """
    result = dict()
    if not len(bdirs):
        bdirs = glob.glob(os.path.join(path, "build-*"))
    else:
        bdirs = [ os.path.join(path, x) for x in bdirs ]
    for bdir in bdirs:
        if os.path.isdir(bdir):
            bname = os.path.basename(bdir)
            dirname = os.path.basename(os.path.dirname(os.path.relpath(bdir, worktree)))
            lst = result.get(bname)
            if not lst:
                result[bname] = list()
            result[bname].append(dirname)
    return result


def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    qiwt     = qibuild.open_worktree(args.worktree)

    if args.force:
        logger.info("preparing to remove:")
    else:
        logger.info("Build directory that will be removed (use -f to apply):")
    folders = dict()
    for project in qiwt.buildable_projects.values():
        result = list_build_folder(project, args.build_directory, qiwt.root)
        for k, v in result.iteritems():
            if folders.get(k):
                folders[k].extend(v)
            else:
                folders[k] = v
    for k, v in folders.iteritems():
        logger.info(k)
        print " ", ",".join(v)
        # for p in v:
        #     print "  %s" % p

    if args.force:
        logger.info("")
        logger.info("removing:")
        for project in qiwt.buildable_projects.values():
            cleanup(project, args.build_directory, qiwt.root, args.force)


