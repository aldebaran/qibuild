## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Install a project and its dependencies """

import os

from qisys import ui
import qisys
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("install options")
    group.add_argument("--prefix", metavar="PREFIX",
        help="value of CMAKE_INSTALL_PREFIX, defaults to '/'")
    group.add_argument("destdir", metavar="DESTDIR")
    group.add_argument("--include-deps", action="store_true", dest="include_deps",
        help="Include dependencies when installing (this is the default)")
    group.add_argument("--no-include-deps", action="store_false", dest="include_deps",
        help="Ignore dependencies when installing (use with caution)")
    group.add_argument("--split-debug", action="store_true", dest="split_debug",
        help="Split the debug symbols out of the binaries")
    parser.set_defaults(runtime=False, prefix="/", include_deps=True)
    if not parser.epilog:
        parser.epilog = ""
    parser.epilog += """
Warning:
    If CMAKE_INSTALL_PREFIX was set during configure, it is necessary to repeat
    it at install using the '--prefix' option.
"""


def do(args):
    """Main entry point"""
    toc = qibuild.toc.toc_open(args.worktree, args)
    # Compute final destination:
    prefix = args.prefix[1:]
    destdir = qisys.sh.to_native_path(args.destdir)
    dest = os.path.join(destdir, prefix)

    # Resolve deps:
    (packages, projects) = qibuild.cmdparse.deps_from_args(toc, args)

    if toc.active_config:
        ui.info(ui.green, "Active configuration: ",
                ui.blue, "%s (%s)" % (toc.active_config, toc.build_type))

    ui.info(ui.green, "The following projects")
    for project in projects:
        ui.info(ui.green, " *", ui.blue, project.name)
    if args.include_deps and packages:
        ui.info(ui.green, "and the following packages")
        for package in packages:
            ui.info(" *", ui.blue, package.name)
    ui.info(ui.green, "will be installed to", ui.blue, dest)
    if args.runtime:
        ui.info(ui.green, "(runtime components only)")

    # Install packages to destdir:
    if args.include_deps and packages:
        print
        ui.info(ui.green, ":: ", "Installing packages")
        for (i, package) in enumerate(packages, start=1):
            ui.info(ui.green, "*", ui.reset, "(%i/%i)" % (i, len(packages)),
                    ui.green, "Installing package", ui.blue, package.name)

            toc.toolchain.install_package(package.name, dest, runtime=args.runtime)
        print

    # Install projects to destdir:
    ui.info(ui.green, ":: ", "Installing projects")
    for (i, project) in enumerate(projects, start=1):
        ui.info(ui.green, "*", ui.reset, "(%i/%i)" % (i, len(projects)),
                ui.green, "Installing project", ui.blue, project.name)
        toc.install_project(project,  args.destdir,
                            prefix=args.prefix, runtime=args.runtime,
                            num_jobs=args.num_jobs,
                            split_debug=args.split_debug)
