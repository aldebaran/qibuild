## Copyright (C) 2011 Aldebaran Robotics
"""Generate a binary sdk"""

#FIXME: maybe we should make --no-compress the default

import os
import logging
import datetime

import qibuild

LOGGER = logging.getLogger(__name__)


def get_package_name(project,
    continuous=False,
    version=None,
    config=None):
    """Get the package name of a project.

    Recognized args are:
      continuous -> append the date the the name of the package
      version    -> if not given, will try to use version.cmake at
                    the root of the project
      config     -> if not given, do nothing, else add this at the end
                    of the package name
    """
    res = [project.name]

    if version:
        res.append(version)
    else:
        # Try to get it from project/version.cmake:
        version = qibuild.project.version_from_directory(project.directory)
        if version:
            res.append(version)

    if continuous:
        now = datetime.datetime.now()
        res.append(now.strftime("%Y-%m-%d-%H-%M"))

    if config:
        res.append(config)

    return "-".join(res)



def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.package_parser(parser)
    parser.add_argument("project", nargs="?")
    parser.add_argument("--no-compress", dest="compress",
        action="store_false",
        help  ="Do not compress the final install directory")
    parser.set_defaults(
        cmake_flags=["CMAKE_INSTALL_PREFIX='/'"],
        compress=True,
        include_deps=False)

def _do(args, build_type):
    """Called by do().
    Once with build_type=release on UNIX.
    Twice with build_type=debug and build_type=release on windows

    Returns the directory to make an archive from
    """
    args.build_type = build_type
    toc      = qibuild.toc_open(args.work_tree, args)
    config = toc.active_config

    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project
    project = toc.get_project(project_name)

    inst_dir = os.path.join(toc.work_tree, "package")

    package_name = get_package_name(
        project,
        continuous=args.continuous,
        config=config,
        version=args.version)

    destdir = os.path.join(inst_dir, package_name)
    qibuild.run_action("qibuild.actions.configure", [project_name, "--no-clean-first"],
        forward_args=args)
    qibuild.run_action("qibuild.actions.make", [project_name],
        forward_args=args)
    qibuild.run_action("qibuild.actions.install", [project_name, destdir],
        forward_args=args)
    return destdir

def do(args):
    """Main entry point"""
    toc = qibuild.toc_open(args.work_tree, args)
    if toc.using_visual_studio and not args.runtime:
        _do(args, "debug")
    destdir = _do(args, "release")

    #TODO warn if dest dir is empty

    if args.compress:
        LOGGER.info("Compressing package")
        archive = qibuild.archive.zip(destdir)
        LOGGER.info("Package generated in %s", archive)
        # Now, clean the destdir.
        qibuild.sh.rm(destdir)
        return archive
    else:
        return destdir


