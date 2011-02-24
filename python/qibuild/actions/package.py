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
    parser.add_argument("project", nargs="?")
    parser.set_defaults(
        cmake_flags=["CMAKE_INSTALL_PREFIX='/'"])

def _do(args, build_type):
    """Called by do().
    Once with build_type=release on UNIX.
    Twice with build_type=debug and build_type=release on windows

    Returns the directory to make an archive from
    """
    args.build_type = build_type
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)
    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project
    project = toc.get_project(project_name)
    inst_dir = os.path.join(project.build_directory, "package")
    destdir = os.path.join(inst_dir, project_name)
    toc.package_project(project, destdir)
    return destdir

def do(args):
    """Main entry point"""
    if sys.platform.startswith("win"):
        _do(args, "debug")
    destdir = _do(args, "release")

    archive = qitools.archive.zip(destdir)
    logger   = logging.getLogger(__name__)
    logger.info("Package generated in %s", archive)
    # Now, clean the destdir.
    qitools.sh.rm(destdir)


