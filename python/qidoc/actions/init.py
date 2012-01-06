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
    parser.add_argument("template_repo")

def do(args):
    """ Main entry point

    """
    qidoc_xml = os.path.join(os.getcwd(), "qidoc.xml")
    to_write = """<qidoc>
    <templates repo="%s" />
</qidoc>
"""
    to_write = to_write % args.template_repo
    with open(qidoc_xml, "w") as fp:
        fp.write(to_write)


