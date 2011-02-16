## Copyright (C) 2011 Aldebaran Robotics
"""Install a project """

import os
import logging
import qibuild
import qitools
import shutil

LOGGER = logging.getLogger(__name__)

def install_package(package_src, destdir, runtime=False):
    """

    """
    if runtime:
        raise NotImplementedError("run")
        return
    LOGGER.debug("Installing %s -> %s", package_src, destdir)
    qitools.sh.mkdir(destdir, recursive=True)
    for (root, dirs, files) in os.walk(package_src):
        new_root = os.path.relpath(root, package_src)
        for file in files:
            file_src = os.path.join(root, file)
            qitools.sh.mkdir(os.path.join(destdir, new_root), recursive=True)
            file_dest = os.path.join(destdir, new_root, file)
            print "-- installing:", file_dest
            shutil.copy(file_src, file_dest)


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("install arguments")
    group.add_argument("destdir", metavar="DESTDIR")
    group.add_argument("--runtime", action="store_true",
        help="install runtime componenents only")
    parser.set_defaults(runtime=False)

def do(args):
    """Main entry point"""
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)

    (project_names, package_names, _) = qibuild.toc.resolve_deps(toc, args, runtime=args.runtime)

    LOGGER.info("Installing %s to %s", ", ".join([n for n in project_names]), args.destdir)
    for project_name in project_names:
        project = toc.get_project(project_name)
        toc.install_project(project,  args.destdir, runtime=args.runtime)

    for package_name in package_names:
        package_src = toc.toolchain.get(package_name)
        dest = os.path.join(args.destdir, args.prefix)
        install_package(package_src, dest, runtime=args.runtime)

