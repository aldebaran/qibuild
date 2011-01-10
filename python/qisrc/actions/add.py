##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

import os
import qisrc
import qitools

"""Add a new project in a qisrc workspace """

def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)
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

    # Create the git worktree in qiworktree by default.
    worktree = qitools.qiworktree.worktree_from_args(args)

    git_src_dir = os.path.join(worktree, name)
    print git_src_dir

    if os.path.exists(git_src_dir):
        raise Exception("'%s' already exists. Try using an other name" % git_src_dir)

    git = qisrc.git.Git(git_src_dir)
    git.clone(url, git_src_dir)

