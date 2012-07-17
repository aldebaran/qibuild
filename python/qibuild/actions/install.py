## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Install a project and its dependencies """

import os
import qibuild.log

import qibuild

LOGGER = qibuild.log.get_logger(__name__)


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
        help="install runtime components only")
    group.add_argument("--include-deps", action="store_true", dest="include_deps",
        help="Include dependencies when installing (this is the default)")
    group.add_argument("--no-include-deps", action="store_false", dest="include_deps",
        help="Ignore dependencies when installing (use with caution)")
    group.add_argument("--split-debug", action="store_true", dest="split_debug",
        help="Split the debug symbols out of the binaries")
    parser.set_defaults(runtime=False, prefix="/", include_deps=True)

def do(args):
    """Main entry point"""
    toc = qibuild.toc_open(args.worktree, args)
    # Compute final destination:
    prefix = args.prefix[1:]
    destdir = qibuild.sh.to_native_path(args.destdir)
    dest = os.path.join(destdir, prefix)

    # Resolve deps:
    (project_names, package_names, _) = toc.resolve_deps(runtime=args.runtime)

    # Install packages to destdir:
    if args.include_deps:
        for package_name in package_names:
            toc.toolchain.install_package(package_name, dest, runtime=args.runtime)

    for project_name in project_names:
        project = toc.get_project(project_name)
        toc.install_project(project,  args.destdir,
                            prefix=args.prefix, runtime=args.runtime,
                            num_jobs=args.num_jobs,
                            split_debug=args.split_debug)
