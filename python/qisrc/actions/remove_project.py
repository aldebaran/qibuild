## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Remove a project from a worktree

"""

import qisrc
import qibuild


def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("src", metavar="PATH",
        help="Path to the project sources")
    parser.add_argument("--from-disk", dest="from_disk", action="store_true",
        help="Also remove project sources from disk")
    parser.set_defaults(from_disk=False)

def do(args):
    """Main entry point"""
    src = args.src
    src = qibuild.sh.to_native_path(src)
    worktree = qisrc.open_worktree(args.worktree)
    worktree.remove_project(src, from_disk=args.from_disk)
