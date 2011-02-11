## Copyright (C) 2011 Aldebaran Robotics

import os
import logging
import qisrc
import qitools

LOGGER = logging.getLogger(__name__)

class ProjectAlreadyExists(Exception):
    """Just a custom exception """
    def __init__(self, url, name, path):
        self.url = url
        self.name = name
        self.path = path

    def __str__(self):
        message = "Error when adding project %s (%s)\n" % (self.url, self.name)
        message += "%s already exists." % self.path
        return message


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
    LOGGER.info("Git clone: %s -> %s", url, git_src_dir)

    if os.path.exists(git_src_dir):
        raise ProjectAlreadyExists(url, name, git_src_dir)

    git = qisrc.git.Git(git_src_dir)
    git.clone(url, git_src_dir)

