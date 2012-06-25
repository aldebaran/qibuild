## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Clean a toolchain cache """

import os
import sys
import qibuild.log

import qibuild
import qitoolchain

LOGGER = qibuild.log.get_logger(__name__)

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("name", nargs="?", metavar="NAME",
        help="Name of the toolchain. Defaults to the current toolchain")
    parser.add_argument("feed", metavar="TOOLCHAIN_FEED",
        help="Optional: path to the toolchain configuration file.\n"
             "If not given, the toolchain will be empty.\n"
             "May be a local file or an url",
        nargs="?")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
        help="Print what would be done")
    parser.add_argument("-f", action="store_false", dest="dry_run",
        help="Do the cleaning")
    parser.set_defaults(dry_run=True)


def do(args):
    """ Main entry point

    """
    tc_name = args.name
    dry_run = args.dry_run

    toc = None
    try:
        toc = qibuild.toc.toc_open(args.worktree)
    except qibuild.toc.TocException:
        pass

    if not tc_name:
        if toc:
            tc_name = toc.active_config
        if not tc_name:
            mess  = "Could not find which toolchain to update\n"
            mess += "Please specify a toolchain name from command line\n"
            mess += "Or edit your qibuild.cfg to set a default config\n"
            raise Exception(mess)

    known_tc_names = qitoolchain.toolchain.get_tc_names()
    if not tc_name in known_tc_names:
        mess  = "No such toolchain: '%s'\n" % tc_name
        mess += "Known toolchains are: %s" % known_tc_names
        raise Exception(mess)


    toolchain = qitoolchain.Toolchain(tc_name)
    tc_cache = toolchain.cache

    dirs_to_rm = os.listdir(tc_cache)
    dirs_to_rm = [os.path.join(tc_cache, x) for x in dirs_to_rm]
    dirs_to_rm = [x for x in dirs_to_rm if os.path.isdir(x)]

    num_dirs = len(dirs_to_rm)
    LOGGER.info("Cleaning cache for %s", tc_name)
    if dry_run:
        print "Would remove %i packages" % num_dirs
        print "Use -f to proceed"
        return

    for (i, dir_to_rm) in enumerate(dirs_to_rm):
        sys.stdout.write("Removing package %i / %i\r" % ((i+1), num_dirs))
        sys.stdout.flush()
        qibuild.sh.rm(dir_to_rm)
    LOGGER.info("Done cleaning cache for %s", tc_name)



