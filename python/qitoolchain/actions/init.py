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
    parser.add_argument("feed", metavar="TOOLCHAIN_FEED",
        help="Optional: path to the toolchain configuration file.\n"
             "May be a local file or an url",
        nargs="?")
    parser.add_argument("--name",
        help="Mandatory if feed was not given")
    parser.add_argument("--default",
        help="Use this toolchain by default in this worktree",
        action="store_true")

def do(args):
    """Main entry point

    """
    feed = args.feed
    name = args.name
    if not feed and not name:
        raise Exception("Please specify a feed or use --name")

    tc_cfg = qibuild.configstore.ConfigStore()
    tc_name = None
    if feed:
        feed_path = qibuild.sh.to_native_path(feed)
        if os.path.exists(feed_path):
            tc_cfg.read(feed_path)
            local = True
        else:
            tc_cfg = qitoolchain.remote.get_remote_config(feed)
            local = False
        tc_name = tc_cfg.get("toolchain.name")
        if not tc_name:
            mess  = "Could not create a toolchain with feed: '%s'\n" % feed
            mess += """The config file should a least contain:
    [toolchain]
    name = <NAME>
    """
            raise Exception(mess)
    else:
        # No feed:
        tc_name = args.name
        local = False


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
        mess = "You need to be in a valid toc worktree to use --default\n"
        mess += "Exception was:\n"
        mess += str(toc_error)
        raise Exception(mess)

    cmake_generator = tc_cfg.get("toolchain.cmake.generator")
    cmake_flags     = tc_cfg.get("toolchain.cmake.flags")
    if tc_file:
        qitoolchain.set_tc_config(tc_name, "file", tc_file)
    if cmake_generator:
        qitoolchain.set_tc_config(tc_name, "cmake.generator", cmake_generator)
    if cmake_flags:
        qitoolchain.set_tc_config(tc_name, "cmake.flags", cmake_flags)

    packages = tc_cfg.get("package", default=dict())
    if not packages:
        qitoolchain.set_tc_config(tc_name, "provides", "")

    cache = qitoolchain.get_tc_cache(tc_name)
    toolchain = qitoolchain.Toolchain(tc_name)

    for package_name in packages.keys():
        package_url = tc_cfg.get("package.%s.url" % package_name)
        if package_url is None:
            LOGGER.error("No url for package %s, skipping", package_name)
            continue
        message = "Getting package %s from %s" % (package_name, package_url)
        archive_path = qitoolchain.remote.download(package_url,
            cache,
            clobber=False,
            message=message)
        toolchain.add_package(package_name, archive_path)

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
