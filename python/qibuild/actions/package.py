## Copyright (C) 2011 Aldebaran Robotics
"""Generate a binary sdk"""

import os
import logging
import shutil
import datetime

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

def get_package_name(project, continuous=False, version=None, arch=None):
    """Get the package name of a project.

    Recognized args are:
      continuous -> append the date the the name of the package
      version    -> if not given, will try to use version.cmake at
                    the root of the project
      arch       -> if not given, do nothing, else add this at the end
                    of the package name
    """
    res = [project.name]

    if not version:
        version = get_project_version(project)
        if version:
            res.append(version)
    else:
        res.append(version)

    if continuous:
        now = datetime.datetime.now()
        res.append(now.strftime("%Y-%m-%d-%H-%M"))

    if arch:
        res.append(arch)

    return "-".join(res)

def get_project_version(project):
    """Try to guess version from the sources of the project.

    Return None if not found.
    """
    version_cmake = os.path.join(project.directory, "version.cmake")
    if not os.path.exists(version_cmake):
        return None
    contents = None
    with open(version_cmake, "r") as fp:
        contents = fp.read()

    import re
    up_name = project.name.upper()
    match = re.match('^set\(%s_VERSION\s+"?(.*?)"?\s*\)' % up_name,
                     contents)
    if not match:
        LOGGER.warning("Invalid version.cmake. Should have a line looking like\n"
           "set(%s_VERSION <VERSION>)",  up_name)
        return None
    return match.groups()[0]


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.package_parser(parser)
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

    package_name = get_package_name(
        project,
        continuous=args.continuous,
        arch=args.arch,
        version=args.version)

    destdir = os.path.join(inst_dir, package_name)
    qitools.run_action("qibuild.actions.configure", [project_name, "--no-clean-first"],
        forward_args=args)
    qitools.run_action("qibuild.actions.make", [project_name],
        forward_args=args)
    qitools.run_action("qibuild.actions.install", [project_name, destdir],
        forward_args=args)
    return destdir

def do(args):
    """Main entry point"""
    toc = qibuild.toc_open(args.work_tree, args, use_env=True)
    if toc.using_visual_studio and not args.runtime:
        _do(args, "debug")
    destdir = _do(args, "release")

    if args.standalone:
        LOGGER.info("Embedding qiBuild in package")
        qibuildize(destdir)

    LOGGER.info("Compressing package")
    archive = qitools.archive.zip(destdir)
    LOGGER.info("Package generated in %s", archive)
    return archive
    # Now, clean the destdir.
    qitools.sh.rm(destdir)


