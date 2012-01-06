## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Init a new qidoc wortree

"""

import os
import shutil

import qibuild
import qidoc.core

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
    parser.add_argument("--work-tree", dest="worktree")

def do(args):
    """ Main entry point

    """
    worktree = args.worktree
    worktree = qidoc.core.find_qidoc_root(worktree)
    if worktree:
        print "Found a worktree in %", worktree, ": nothing to do"
        return
    qidoc_xml = os.path.join(os.getcwd(), "qidoc.xml")
    if not os.path.exists(qidoc_xml):
        with open(qidoc_xml, "w") as fp:
            fp.write("<qidoc />")

