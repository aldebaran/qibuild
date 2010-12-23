"""Install a project """

import os
import logging
import qibuild


def install_project(args, project):
    r"""Build a project.

    /!\ assumes that set_build_configs has been called
    """
    pass


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.shell.toc_parser(parser)
    qibuild.shell.project_parser(parser)
    qibuild.shell.build_parser(parser)
    group = parser.add_argument_group("install arguments")
    group.add_argument("--prefix", dest="install_prefix",  help="Install prefix")
    group.add_argument("destdir", metavar="DESTDIR")
    # Force use_deps to be false, because we want to install
    # only the runtime dependencies by default.
    parser.set_defaults(use_deps=False, install_prefix="/usr/local")


def do(args):
    """Main entry point"""
    logger = logging.getLogger(__name__)
    toc = qibuild.toc.toc_open(args)

    projects = qibuild.shell.get_projects(args, toc, args.projects)
    project_names = [p.name for p in projects]

    dest = os.path.join(args.destdir, args.install_prefix[1:])
    logger.info("Installing %s to %s", ", ".join(project_names), dest)

    # Set build configurations
    qibuild.shell.buildaction.set_build_configs(args, toc, projects)

    # Run cmake just to set the install prefix:
    for project in projects:
        new_flags = ["CMAKE_INSTALL_PREFIX=%s" % args.install_prefix]
        # Force args.cmake_flags
        args.cmake_flags = new_flags
        qibuild.shell.buildaction.run_cmake(args, project)

        # Force args.target:
        build_dir = project.cmake.get_build_dir()

        cmd = ["make", "install"]
        # Add DEST_DIR to os.environ:
        build_environ = os.environ.copy()  # Let's not modify os.environ gloablly !
        build_environ["DESTDIR"] = args.destdir
        qibuild.command.check_call(cmd, cwd=build_dir, env=build_environ)
