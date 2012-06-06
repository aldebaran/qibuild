## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Generate a binary sdk"""

import os
import sys
import logging

import qibuild

LOGGER = logging.getLogger(__name__)


def get_package_name(project,
    version=None,
    config=None):
    """Get the package name of a project.

    Recognized args are:
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

    if config:
        res.append(config)

    return "-".join(res)



def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")
    group = parser.add_argument_group("package options")
    group.add_argument("--version", help="Version of the package. "
        "Default is read from the version.cmake file")
    group.add_argument("--runtime", action="store_true",
        help="Install runtime components only")
    parser.add_argument("--internal", dest="internal",
        action="store_true",
        help = "Include internal libs in package")
    group.add_argument("--include-deps", action="store_true", dest="include_deps",
        help="Include dependencies when making the package (off by the default)")
    parser.set_defaults(
        cmake_flags=["CMAKE_INSTALL_PREFIX='/'"],
        compress=True,
        include_deps=False,
        internal=False,
        continuous=False,
        runtime=False)

def _do_package(args, project_name, destdir, debug):
    """ Helper function used on windows.
    We need both debug and release in the package,
    otherwize the package is not usable to compile
    something else

    """
    if debug:
        build_args = ["--debug",  project_name]
    else:
        build_args = ["--release", project_name]

    qibuild.run_action("qibuild.actions.configure", build_args + ["--no-clean-first"],
        forward_args=args)
    qibuild.run_action("qibuild.actions.make", build_args,
        forward_args=args)
    qibuild.run_action("qibuild.actions.install", build_args + [destdir],
        forward_args=args)

def do(args):
    """Main entry point"""
    toc = qibuild.toc_open(args.work_tree, args)
    config = toc.active_config
    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project
    project = toc.get_project(project_name)
    package_name = get_package_name(project,
        version=args.version, config=config)
    destdir = os.path.join(toc.work_tree, "package")
    destdir = os.path.join(destdir, package_name)

    if args.internal:
        args.cmake_flags.append('QI_INSTALL_INTERNAL=ON')

    if sys.platform.startswith("win") and not args.runtime:
        # Ignore the --release flag and always build in debug and in release:
        _do_package(args, project_name, destdir, debug=True)
        _do_package(args, project_name, destdir, debug=False)
    else:
        qibuild.run_action("qibuild.actions.configure", [project_name, "--no-clean-first"],
            forward_args=args)
        qibuild.run_action("qibuild.actions.make", [project_name],
            forward_args=args)
        qibuild.run_action("qibuild.actions.install", [project_name, destdir],
            forward_args=args)


    if args.compress:
        LOGGER.info("Compressing package")
        archive = qibuild.archive.zip(destdir)
        LOGGER.info("Package generated in %s", archive)
        # Now, clean the destdir.
        qibuild.sh.rm(destdir)
        return archive
    else:
        return destdir

