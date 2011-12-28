## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
    qibuild.worktree.work_tree_parser(parser)
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
                qibuild.sh.rm(bdir)

def list_build_folder(path, bdirs, work_tree):
    """ list all buildable directory """
    result = dict()
    if not len(bdirs):
        bdirs = glob.glob(os.path.join(path, "build-*"))
    else:
        bdirs = [ os.path.join(path, x) for x in bdirs ]
    for bdir in bdirs:
        if os.path.isdir(bdir):
            bname = os.path.basename(bdir)
            dirname = os.path.basename(os.path.dirname(os.path.relpath(bdir, work_tree)))
            lst = result.get(bname)
            if not lst:
                result[bname] = list()
            result[bname].append(dirname)
    return result


def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    qiwt     = qibuild.worktree_open(args.work_tree)

    if args.force:
        logger.info("preparing to remove:")
    else:
        logger.info("Build directory that will be removed (use -f to apply):")
    folders = dict()
    for project in qiwt.buildable_projects.values():
        result = list_build_folder(project, args.build_directory, qiwt.work_tree)
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
            cleanup(project, args.build_directory, qiwt.work_tree, args.force)


