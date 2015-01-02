## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Add a new project to a worktree """

import os

import qisys
import qisys.parsers
import qisrc.git


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
    parser.set_defaults(branch="master")

def do(args):
    """Main entry point"""
    worktree = qisys.parsers.get_worktree(args)
    if os.path.exists(args.path_or_url):
        path = args.path_or_url
        path = qisys.sh.to_native_path(path)
        worktree.add_project(path)
        return
    url = args.path_or_url
    src = args.src
    if not src:
        gitname = qisrc.git.name_from_url(url)
        src = gitname.replace(".git", "")
        src = os.path.join(os.getcwd(), src)
    worktree.add_project(src)
    worktree_proj = worktree.get_project(src)
    proj_path = worktree_proj.path
    if os.path.exists(proj_path):
        raise Exception("%s already exists" % proj_path)
    git = qisrc.git.Git(proj_path)
    git.clone(url, "--branch", args.branch)
