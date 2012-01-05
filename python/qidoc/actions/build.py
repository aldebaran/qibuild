## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Build documentation

"""


import os
import shutil

import qibuild
import qidoc.core

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
    parser.add_argument("--work-tree", dest="worktree")
    parser.add_argument("output_dir", nargs="?",
        help="Where to generate the docs")
    parser.add_argument("--version")


def do(args):
    """ Main entry point

    """
    output_dir = args.output_dir
    worktree = args.worktree
    worktree = qidoc.core.find_qidoc_root(worktree)
    if not worktree:
        raise Exception("No qidoc worktree found.\n"
          "Please call qidoc init or go to a qidoc worktree")

    if not output_dir:
        output_dir = os.path.join(worktree, "build-doc")

    builder = qidoc.core.QiDocBuilder(worktree, output_dir)
    opts = dict()
    opts["version"] = "0.42"
    builder.build(opts)


