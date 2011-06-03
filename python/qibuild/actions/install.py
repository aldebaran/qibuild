## Copyright (C) 2011 Aldebaran Robotics
"""Install a project """

import os
import sys
import logging

import qibuild
import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)

def is_runtime(filename):
    basename = os.path.basename(filename)
    basedir  = filename.split(os.path.sep)[0]
    if filename.startswith("bin"):
        if sys.platform.startswith("win"):
            if filename.endswith(".exe"):
                return True
            if filename.endswith(".dll"):
                return True
            else:
                return False
        else:
            return True
    if filename.startswith("lib"):
        # exception for python:
        if "python" in filename and filename.endswith("Makefile"):
            return True
        # shared libraries
        shared_lib_ext = ""
        if sys.platform.startswith("win"):
            shared_lib_ext = ".dll"
        if sys.platform == "linux2":
            shared_lib_ext = ".so"
        if sys.platform == "darwing":
            shared_lib_ext = ".dylib"
        if shared_lib_ext in basename:
            return True
        # python
        if basename.endswith(".py"):
            return True
        if basename.endswith(".pyd"):
            return True
        else:
            return False
    if filename.startswith(os.path.join("share", "cmake")):
        return False
    if filename.startswith(os.path.join("share", "man")):
        return False
    if basedir == "share":
        return True
    if basedir == "include":
        # exception for python:
        if filename.endswith("pyconfig.h"):
            return True
        else:
            return False
    if basedir.endswith(".framework"):
        return True

    # True by default: better have too many stuff than
    # not enough
    return True

def install_package(package_src, destdir, runtime=False):
    """Install a package to a desdir.

    """
    if runtime:
        qibuild.sh.install(package_src, destdir, filter=is_runtime)
    else:
        qibuild.sh.install(package_src, destdir)

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
    group.add_argument("--no-rdeps", action="store_false", dest="rdeps",
        help="ignore runtime dependencies. Use with caution.")
    parser.set_defaults(runtime=False, prefix="/", rdeps=True)

def do(args):
    """Main entry point"""
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)

    (project_names, package_names, _) = qibuild.toc.resolve_deps(toc, args, runtime=args.runtime)

    # Why do we call cmake here?

    # If CMAKE_INSTALL_PREFIX was never set by the user, it
    # defaults to /usr/local.
    # If the destdir given by the user is /tmp/foo/, files will be installed in
    # /tmp/foo/usr/local.

    # So, if we want packages to be installed to /tmp/usr/local too we need to
    # know what was the value of CMAKE_INSTALL_PREFIX, and better be sure
    # that it has the same value for every project.

    # A simple way to do this is to re-call cmake on every dependency,
    # without cleaning the cache (or else we would use user's previous
    # settings)

    # DESTDIR=/tmp/foo and CMAKE_PREFIX="/usr/local" means
    # dest = /tmp/foo/usr/local
    prefix = args.prefix[1:]
    dest = os.path.join(args.destdir, prefix)
    LOGGER.info("Setting CMAKE_INSTALL_PREFIX=%s on every project", args.prefix)
    for project_name in project_names:
        project = toc.get_project(project_name)
        qibuild.cmake(project.directory, project.build_directory,
            ['-DCMAKE_INSTALL_PREFIX=%s' % args.prefix],
            clean_first=False)

    if project_names:
        LOGGER.info("Installing %s to %s", ", ".join([n for n in project_names]), dest)
    for project_name in project_names:
        project = toc.get_project(project_name)
        toc.install_project(project,  args.destdir, runtime=args.runtime)

    if not args.rdeps:
        return

    if package_names:
        LOGGER.info("Installing %s to %s", ", ".join([p for p in package_names]), dest)
    for package_name in package_names:
        package_src = toc.toolchain.get(package_name)
        install_package(package_src, dest, runtime=args.runtime)

