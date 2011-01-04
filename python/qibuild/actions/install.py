"""Install a project """

import logging
import qibuild

def install_project(args, project):
    r"""Build a project.

    /!\ assumes that set_build_configs has been called
    """
    pass

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("install arguments")
    group.add_argument("destdir", metavar="DESTDIR")
    # Force use_deps to be false, because we want to install
    # only the runtime dependencies by default.
    parser.set_defaults(use_deps=False)

def do(args):
    """Main entry point"""
    logger = logging.getLogger(__name__)
    toc      = qibuild.toc.open(args.work_tree, args, use_env=True)

    wanted_projects = qibuild.toc.get_projects_from_args(toc, args)
    (src_projects, bin_projects, not_found_projects) = toc.split_sources_and_binaries(wanted_projects)

    logger.info("Installing %s to %s", ", ".join(src_projects), args.destdir)
    for project in src_projects:
        qibuild.project.install(toc.projects[project], args.destdir)
