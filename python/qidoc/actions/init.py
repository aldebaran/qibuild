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
    parser.add_argument("qidoc_xml",
        help="Path to a qidox.xml file")


def do(args):
    """ Main entry point

    """
    worktree = args.worktree
    xml_in   = args.qidoc_xml
    worktree = qidoc.core.find_qidoc_root(worktree)
    if worktree:
        print "Found a worktree in %", worktree, ": nothing to do"
        return
    qidoc_xml = os.path.join(os.getcwd(), "qidoc.xml")
    shutil.copy(xml_in, qidoc_xml)

