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
    toc      = qibuild.toc_open(args.work_tree, args, use_env=True)
    (project_names, package_names, not_found) = qibuild.toc.resolve_deps(toc, args)
    inst_dir = os.path.join(toc.work_tree, "bdist")
    for project_name in project_names:
        project = toc.get_project(project_name)
        destdir = os.path.join(inst_dir, project_name)
        logger.info("Generating bin sdk for %s in %s", project_name, inst_dir)
        toc.configure_project(project)
        toc.build_project(project)
        toc.install_project(project, destdir)
        archive = qitools.archive.zip_unix(destdir)
        logger.info("Archive generated in %s", archive)

