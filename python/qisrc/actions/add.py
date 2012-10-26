## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Add a new project to a worktree """

import os

from qisys import ui
import qisrc.sync
import qisys
import qisys.parsers


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("path_or_url",  metavar="[URL|PATH]",
                        help="git url or path of project")
    group = parser.add_argument_group("git options")
    group.add_argument("--src", help="Where to clone the project. "
                        "If not given, will be guessed from the git url "
                        "and the working dir")
    group.add_argument("-b", "--branch")

def do(args):
    """Main entry point"""
    worktree = qisys.worktree.open_worktree(args.worktree)
    ui.info(ui.green, "Current worktree:", ui.reset, ui.bold, worktree.root)
    if os.path.exists(args.path_or_url):
        path = args.path_or_url
        path = qisys.sh.to_native_path(path)
        worktree.add_project(path)
        return
    url = args.path_or_url
    src = args.src
    if not src:
        gitname = url.split("/")[-1].replace(".git", "")
        src = os.path.join(os.getcwd(), gitname)
    qisrc.sync.clone_project(worktree, url, src=src, branch=args.branch)
