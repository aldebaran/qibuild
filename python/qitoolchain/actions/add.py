## Copyright (C) 2011 Aldebaran Robotics

"""Add a new package in a toolchain dir
"""

import os
import shutil
import logging

import qitools
import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project_or_package_path", nargs="?",
        help="Name of the project to package, or path to an existing package")

def do(args):
    """ Add a project to the current toolchain

    - Check that there is a current toolchain
    - Run `qibuild package' if a project, and not a package was given as
        argument
    - Add the package to the cache
    - Add the package from cache to toolchain

    """
    toc = qibuild.toc.toc_open(args.work_tree, args, use_env=True)

    tc_name = toc.toolchain_name
    if tc_name is None:
        raise Exception("Could not find current toolchain")

    if not args.project_or_package_path:
        project_name = qibuild.toc.project_from_cwd()
    else:
        if os.path.exists(args.project_or_package_path):
            package = args.project_or_package_path
            project_name = os.path.basename(package)
            project_name = qitools.archive.extracted_name(project_name)
        else:
            project_name = args.project_or_package_path
            package = qitools.cmdparse.run_action("qibuild.actions.package",
                [project_name], forward_args=args)

    tc_cache_path = qitoolchain.get_tc_cache(tc_name)
    qitools.sh.mkdir(tc_cache_path, recursive=True)
    in_cache = os.path.join(tc_cache_path, os.path.basename(package))
    shutil.copy(package, in_cache)

    tc = qitoolchain.Toolchain(tc_name)
    tc.add_package(project_name, in_cache)
