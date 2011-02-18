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
    qibuild.parsers.project_parser(parser)
    parser.set_defaults(
        cmake_flags=["CMAKE_INSTALL_PREFIX='/'"])

def _do(args, build_type):
    """Called by do().
    Once with build_type=release on UNIX.
    Twice with build_type=debug and build_type=release on windows

    """
    args.build_type = build_type
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)
    (project_names, package_names, not_found) = qibuild.toc.resolve_deps(toc, args)
    inst_dir = os.path.join(toc.work_tree, "package")
    for project_name in project_names:
        project = toc.get_project(project_name)
        destdir = os.path.join(inst_dir, project_name)
        logger.info("Generating bin sdk for %s in %s", project_name, inst_dir)
        toc.package_project(project, destdir)
        archive = qitools.archive.zip(destdir)
        logger.info("Archive generated in %s", archive)

def do(args):
    """Main entry point"""
    if sys.platform.startswith("win"):
        _do(args, "debug")
    _do(args, "release")


