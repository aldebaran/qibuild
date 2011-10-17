## Copyright (C) 2011 Aldebaran Robotics

""" Configure a worktree to use a toolchain.

Toolchain packages and known configurations will be fetched from an URL.

"""

import os
import logging

import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)

KNOWN_CONFIGS = [
    'linux32',
    'mac32',
    'win32-vs2008',
    'win32-vs2010',
    'geode',
    'atom']


def configure_parser(parser):
    """Configure parse for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("feed", metavar="TOOLCHAIN FEED",
        help="Optional: path to the toolchain configuration file.\n"
             "May be a local file or an url")
    parser.add_argument("--name",
        help="Name of the toolchain to create.\n"
             "Mandatory if no toolchain configuration file was given")
    parser.add_argument("--default",
        help="Use this toolchain by default in this worktree",
        action="store_true")

def do(args):
    """Main entry point

    """
    feed = args.feed
    tc_name = args.name
    if not tc_name and not feed:
        raise Exception("Please use at specify a feed or use --name")

    feed_path = qibuild.sh.to_native_path(feed)
    if os.path.exists(feed_path):
        tc_cfg = qibuild.configstore.ConfigStore()
        tc_cfg.read(feed_path)
        local = True
    else:
        tc_cfg = qitoolchain.remote.get_remote_config(feed)
        local = False


    if not tc_name:
        tc_name = tc_cfg.get("toolchain.name")


    tc_file = None
    if local:
        tc_root = os.path.dirname(feed_path)
        tc_file = tc_cfg.get("toolchain.toolchain_file")
        if tc_file:
            tc_file = os.path.join(tc_root, tc_file)
    else:
        tc_file = None

    toc_error = None
    toc = None
    try:
        toc = qibuild.toc.toc_open(args.work_tree)
    except qibuild.toc.TocException, e:
        toc_error = e

    if args.default and not toc:
        mess = "You need to be in a toc worktree to use --default\n"
        mess += toc_error
        raise Exception(mess)

    cmake_generator = tc_cfg.get("toolchain.cmake.generator")
    cmake_flags     = tc_cfg.get("toolchain.cmake.flags")
    if tc_file:
        qitoolchain.set_tc_config(tc_name, "file", tc_file)
    if cmake_generator:
        qitoolchain.set_tc_config(tc_name, "cmake.generator", cmake_generator)
    if cmake_flags:
        qitoolchain.set_tc_config(tc_name, "cmake.flags", cmake_flags)

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
