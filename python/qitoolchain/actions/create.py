## Copyright (C) 2011 Aldebaran Robotics

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


def do(args):
    """Main entry point

    """
    feed = args.feed
    tc_name = args.name

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

    toolchain = qitoolchain.Toolchain(tc_name)
    if tc_name in qitoolchain.get_tc_names():
        LOGGER.info("%s already exists, creating a new one", tc_name)
        toolchain.remove()
        toolchain = qitoolchain.Toolchain(tc_name)
    if feed:
        toolchain.parse_feed(feed)

    if args.cmake_generator:
        toc.update_config("cmake.generator", args.cmake_generator, tc_name)
    if args.default:
        toc.update_config("config", tc_name)
        LOGGER.info("Now using toolchain %s by default", tc_name)
    else:
        mess = """Now try using:
    qibuild configure -c {tc_name}
    qibuild make      -c {tc_name}
"""
        mess = mess.format(tc_name=tc_name)
        LOGGER.info(mess)
