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
    parser.add_argument("project", nargs="?")

def do(args):
    """ Add a project to the current toolchain

    - Check that there is a current toolchain
    - Run `qibuild package'
    - Add the package to the cache
    - Add the package from cache to toolchain

    """
    toc = qibuild.toc.toc_open(args.work_tree, args, use_env=True)
    if toc.toolchain.name == "system":
        raise Exception("Could not find current toolchain.\n"
            "Please use a --toolchain option or edit configuration file")

    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project

    package = qitools.cmdparse.run_action("qibuild.actions.package",
        [project_name], forward_args=args)

    tc_cache_path = qitoolchain.get_tc_cache(toc.toolchain.name)
    qitools.sh.mkdir(tc_cache_path, recursive=True)
    in_cache = os.path.join(tc_cache_path, os.path.basename(package))
    shutil.copy(package, in_cache)

    toc.toolchain.add_package(project_name, in_cache)
