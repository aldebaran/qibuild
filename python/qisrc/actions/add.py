## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Add a new project in a qisrc workspace """

import os
import logging
import qisrc
import qibuild

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("url",  metavar="URL", help="url of the project. "
        "right now only git URLs are supported")
    parser.add_argument("name", metavar="NAME", nargs="?",
        help="name of the project. If not given, this will be deduced from the "
             "URL")
    parser.add_argument("--path",
        help="path to the project. If not given, the project will be put in "
             "<QI_WORK_TREE>/<name>")


def do(args):
    """Main entry point"""
    worktree = qibuild.worktree.open_worktree(args.worktree)

    url = args.url
    name = args.name
    path = args.path
    if not name:
        name = url.split("/")[-1].replace(".git", "")
    if not path:
        path = os.path.join(worktree.root, name)
    else:
        path = os.path.join(worktree.root, path)

    git_src_dir = os.path.join(path, name)
    LOGGER.info("Git clone: %s -> %s", url, git_src_dir)

    if os.path.exists(git_src_dir):
        mess  = "Could not add project %s from %s\n" % (name, url)
        mess += "%s already exists\n" % git_src_dir
        mess += "Please choose another name or another path"
        raise Exception(mess)

    git = qisrc.git.Git(git_src_dir)
    git.clone(url)

    worktree.add_project(name, git_src_dir)

