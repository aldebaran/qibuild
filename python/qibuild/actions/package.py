## Copyright (C) 2011 Aldebaran Robotics
"""Generate a binary sdk"""

import os
import sys
import logging
import shutil

import qitools
import qibuild

LOGGER = logging.getLogger(__name__)

def qibuildize(destdir):
    """Make sure the package is usable even without qibuild installed.

    """
    # First, create the toolchain.cmake file :
    src  = os.path.join(qibuild.CMAKE_QIBUILD_DIR, "templates", "toolchain-pc.cmake")
    dest = os.path.join(destdir, "toolchain-pc.cmake")
    shutil.copy(src, dest)

    # Then, install the qibuild/cmake files inside the package:
    src  = os.path.join(qibuild.CMAKE_QIBUILD_DIR)
    dest = os.path.join(destdir, "share", "cmake", "qibuild")
    qitools.sh.install(src, dest)

    # Lastly, install qibuild/version.cmake at the root of the SDK:
    src  = os.path.join(qibuild.CMAKE_QIBUILD_DIR, "version.cmake")
    dest = os.path.join(destdir, "share", "cmake", "qibuild", "qibuild-version.cmake")
    qitools.sh.install(src, dest)


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")
    parser.add_argument("--standalone", action="store_true",
        help="make a standalone package. "
        "This will package qibuild inside your package, and create a toolchain "
        "file for others to use your pacakge")
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
    qitools.run_action("qibuild.actions.configure", [project_name],
        forward_args=args)
    qitools.run_action("qibuild.actions.make", [project_name],
        forward_args=args)
    qitools.run_action("qibuild.actions.install", [project_name, destdir],
        forward_args=args)
    return destdir

def do(args):
    """Main entry point"""
    if sys.platform.startswith("win"):
        _do(args, "debug")
    destdir = _do(args, "release")

    if args.standalone:
        LOGGER.info("Embedding qiBuild in package")
        qibuildize(destdir)

    LOGGER.info("Compressing package")
    archive = qitools.archive.zip(destdir)
    LOGGER.info("Package generated in %s", archive)
    # Now, clean the destdir.
    qitools.sh.rm(destdir)


