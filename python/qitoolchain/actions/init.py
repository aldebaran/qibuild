## Copyright (C) 2011 Aldebaran Robotics

""" Configure a worktree to use a toolchain.

Toolchain packages and known configurations will be fetched from an URL.

"""

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
    parser.add_argument("name",
        help="Name of the toolchain")
    parser.add_argument("feed", metavar="TOOLCHAIN_FEED",
        help="Optional: path to the toolchain configuration file.\n"
             "If not given, the toolchain will be empty.\n"
             "May be a local file or an url",
        nargs="?")
    parser.add_argument("--arch",
        help="Specify an architecture to use")
    parser.add_argument("--default",
        help="Use this toolchain by default in this worktree",
        action="store_true")

"""
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
"""


def do(args):
    """Main entry point

    """
    feed = args.feed
    tc_name = args.name

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

    toolchain = qitoolchain.Toolchain(tc_name)
    if feed:
        toolchain.update_from_feed(feed)

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
