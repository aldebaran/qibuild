## Copyright (C) 2011 Aldebaran Robotics
"""Generate a binary sdk"""

import os
import sys
import logging

import qitools
import qibuild


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project_name")
    parser.set_defaults(
        cmake_flags=["CMAKE_INSTALL_PREFIX='/'"])

def _do(args, project_name, destdir, build_type):
    """Called by do().
    Once with build_type=release on UNIX.
    Twice with build_type=debug and build_type=release on windows

    """
    args.build_type = build_type
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)
    project = toc.get_project(project_name)
    toc.package_project(project, destdir)

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    project_name = args.project_name
    work_tree = qitools.qiworktree.worktree_from_args(args)
    inst_dir = os.path.join(work_tree, "package")
    destdir = os.path.join(inst_dir, project_name)
    logger.info("Generating bin sdk for %s in %s", project_name, inst_dir)

    if sys.platform.startswith("win"):
        _do(args, project_name, destdir, "debug")
    _do(args, project_name, destdir, "release")

    archive = qitools.archive.zip(destdir)
    logger.info("Archive generated in %s", archive)


