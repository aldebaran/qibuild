"""Generate a binary sdk"""

import logging
import os
import qitools
import qibuild


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.set_defaults(
        use_deps=False,
        debug=False,
        cmake_flags=["CMAKE_INSTALL_PREFIX='/'"])

def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc.open(args.work_tree, args, use_env=True)
    wanted_projects = qibuild.toc.get_projects_from_args(toc, args)
    (src_projects, bin_projects, not_found_projects) = toc.split_sources_and_binaries(wanted_projects)
    inst_dir = os.path.join(toc.work_tree, "bdist")
    for project_name in wanted_projects:
        project = toc.projects[project_name]
        logger.info("Generating bin sdk for %s in %s", project_name, inst_dir)
        qibuild.project.configure(project)
        qibuild.project.make(project, "release")
        destdir = os.path.join(inst_dir, project_name)
        qibuild.project.install(project, destdir)
        archive = qitools.archive.zip_unix(destdir)
        logger.info("Archive generated in %s", archive)

