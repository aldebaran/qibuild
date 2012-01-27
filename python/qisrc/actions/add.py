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
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("url",  metavar="URL", help="url of the project. "
        "right now only git URLs are supported")
    parser.add_argument("name", metavar="NAME", nargs="?",
        help="name of the project. If not given, this will be deduced from the "
             "URL")


def do(args):
    """Main entry point"""
    url = args.url
    name = args.name
    if not name:
        name = url.split("/")[-1].replace(".git", "")

    work_tree = qibuild.worktree.worktree_open(args.work_tree)

    git_src_dir = os.path.join(work_tree.work_tree, name)
    LOGGER.info("Git clone: %s -> %s", url, git_src_dir)

    if os.path.exists(git_src_dir):
        raise qibuild.worktree.ProjectAlreadyExists(url, name, git_src_dir)

    git = qisrc.git.Git(git_src_dir)
    git.clone(url, git_src_dir)

