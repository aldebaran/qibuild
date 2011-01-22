"""Install a project """

import os
import logging
import qibuild

def run_time_install(package_src, destdir):
    """

    """
    # FIXME: implement :)
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
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)

    (project_names, package_names, _) = qibuild.toc.resolve_deps(toc, args, runtime=True)

    print project_names, package_names
    logger.info("Installing %s to %s", ", ".join([n for n in project_names]), args.destdir)
    for project_name in project_names:
        project = toc.get_project(project_name)
        toc.install_project(project,  args.destdir)

    for package_name in package_names:
        package_src = toc.toolchain.get(package_name)
        run_time_install(package_src, args.destdir)

