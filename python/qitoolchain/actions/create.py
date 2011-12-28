## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Configure a worktree to use a toolchain.

Toolchain packages and known configurations will be fetched from an URL.

"""

import logging

import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("name", metavar="NAME",
        help="Name of the toolchain")
    parser.add_argument("feed", metavar="TOOLCHAIN_FEED",
        help="Optional: path to the toolchain configuration file.\n"
             "If not given, the toolchain will be empty.\n"
             "May be a local file or an url",
        nargs="?")
    parser.add_argument("--default",
        help="Use this toolchain by default in this worktree",
        action="store_true")
    parser.add_argument("--cmake-generator",
        help="CMake generator to use when using this toolchain",
        choices=qibuild.KNOWN_CMAKE_GENERATORS)
    parser.add_argument("--dry-run", action="store_true",
        help="Print what would be done")

def do(args):
    """Main entry point

    """
    feed = args.feed
    tc_name = args.name
    dry_run = args.dry_run

    # Validate the name: must be a valid filename:
    bad_chars = r'<>:"/\|?*'
    for bad_char in bad_chars:
        if bad_char in tc_name:
            mess  = "Invalid toolchain name: '%s'\n" % tc_name
            mess += "A vaild toolchain name should not contain any "
            mess += "of the following chars:\n"
            mess += " ".join(bad_chars)
            raise Exception(mess)


    toc_error = None
    toc = None
    try:
        toc = qibuild.toc.toc_open(args.work_tree)
    except qibuild.toc.TocException, e:
        toc_error = e

    if args.default and not toc:
        mess = "You need to be in a valid toc worktree to use --default\n"
        mess += "Exception was:\n"
        mess += str(toc_error)
        raise Exception(mess)

    if args.cmake_generator and not toc:
        mess = "You need to be in a valid toc worktree to use --cmake-generator\n"
        mess += "Exception was:\n"
        mess += str(toc_error)
        raise Exception(mess)

    if tc_name in qitoolchain.get_tc_names():
        LOGGER.info("%s already exists, creating a new one", tc_name)
        toolchain = qitoolchain.Toolchain(tc_name)
        toolchain.remove()

    toolchain = qitoolchain.Toolchain(tc_name)
    if feed:
        toolchain.parse_feed(feed, dry_run=dry_run)

    config = None
    cmake_generator = args.cmake_generator
    if toc:
        matching_conf = toc.configstore.configs.get(tc_name)
        if matching_conf:
            matching_conf.cmake.generator = cmake_generator
        else:
            config = qibuild.config.Config()
            config.name = tc_name
            toc.configstore.add_config(config)
        toc.save_config()
    if args.default:
        toc.configstore.set_default_config(tc_name)
        toc.save_config()
        LOGGER.info("Now using toolchain %s by default", tc_name)
    else:
        mess = """Now try using:
    qibuild configure -c {tc_name}
    qibuild make      -c {tc_name}
"""
        mess = mess.format(tc_name=tc_name)
        LOGGER.info(mess)
