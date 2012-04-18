## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Add a new project in a qisrc workspace """

import qisrc.sync
import qibuild



def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("url",  metavar="URL", help="url of the project. "
        "right now only git URLs are supported")
    parser.add_argument("--src",
        help="path to the source of project. (Relative to the worktree). "
             "If not given, the project will be put in "
             "<QI_WORK_TREE>/<name>")

def do(args):
    """Main entry point"""
    worktree = qisrc.worktree.open_worktree(args.worktree)
    qisrc.sync.clone_project(worktree, args.url,
                             src=args.src,
                             skip_if_exists=False)
