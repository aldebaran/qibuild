## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Install a project """

import os
import logging

import qibuild

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("install arguments")
    group.add_argument("--prefix", metavar="PREFIX",
        help="value of CMAKE_INSTALL_PREFIX, defaults to '/'")
    group.add_argument("destdir", metavar="DESTDIR")
    group.add_argument("--runtime", action="store_true",
        help="install runtime componenents only")
    group.add_argument("--include-deps", action="store_true", dest="include_deps",
        help="Include dependencies when installing (this is the default)")
    group.add_argument("--no-include-deps", action="store_false", dest="include_deps",
        help="Ignore dependencies when installing (use with caution)")
    parser.set_defaults(runtime=False, prefix="/", include_deps=True)

def do(args):
    """Main entry point"""
    toc      = qibuild.toc_open(args.work_tree, args)

    (project_names, package_names, _) = toc.resolve_deps(runtime=args.runtime)

    # Why do we call cmake here?

    # If CMAKE_INSTALL_PREFIX was never set by the user, it
    # defaults to /usr/local.
    # If the destdir given by the user is /tmp/foo/, files will be installed in
    # /tmp/foo/usr/local.

    # So, if we want packages to be installed to /tmp/usr/local too we need to
    # know what was the value of CMAKE_INSTALL_PREFIX, and better be sure
    # that it has the same value for every project.

    # A simple way to do this is to re-call cmake on every dependency,
    # without cleaning the cache (or else we would not use user's previous
    # settings)

    # DESTDIR=/tmp/foo and CMAKE_PREFIX="/usr/local" means
    # dest = /tmp/foo/usr/local
    prefix = args.prefix[1:]
    destdir = qibuild.sh.to_native_path(args.destdir)
    dest = os.path.join(args.destdir, prefix)
    dest = qibuild.sh.to_native_path(dest)
    LOGGER.info("Setting CMAKE_INSTALL_PREFIX=%s on every project", args.prefix)
    for project_name in project_names:
        project = toc.get_project(project_name)
        # note: cmake will emit warnings at this time when using NMake makefiles
        # because LIBPATH, INCLUDE et al. are not set.
        # this is because we do NOT mess with os.environ ...
        # This is why we need to re-read env from toc.build_env so that no warning
        # appears.
        qibuild.cmake.cmake(project.directory, project.build_directory,
            ['-DCMAKE_INSTALL_PREFIX=%s' % args.prefix],
            clean_first=False,
            env=toc.build_env)

    if not args.include_deps:
        project_names = [project_name]

    if project_names:
        LOGGER.info("Installing %s to %s (%s)", ", ".join([n for n in project_names]), dest, toc.build_type)
    for project_name in project_names:
        project = toc.get_project(project_name)
        # Build target preinstall on the project (not always called for some reason)
        if not toc.using_visual_studio and not toc.cmake_generator == "Xcode":
            toc.build_project(project, target="preinstall")
        toc.install_project(project,  destdir, runtime=args.runtime)

    if not args.include_deps:
        return

    if package_names:
        LOGGER.info("Installing %s to %s (%s)", ", ".join([p for p in package_names]), dest, toc.build_type)
    for package_name in package_names:
        toc.toolchain.install_package(package_name, dest, runtime=args.runtime)

