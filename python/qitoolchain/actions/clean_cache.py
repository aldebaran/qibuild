## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Clean a toolchain cache """

import os
import sys

from qisys import ui
import qisys
import qisys.parsers
import qitoolchain


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("name", nargs="?", metavar="NAME",
        help="Name of the toolchain")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
        help="Print what would be done")
    parser.add_argument("-f", "--force", action="store_false", dest="dry_run",
        help="Do the cleaning")
    parser.set_defaults(dry_run=True)


def do(args):
    """ Main entry point

    """
    dry_run = args.dry_run
    tc = qitoolchain.get_toolchain(args.name)
    tc_cache = tc.cache

    dirs_to_rm = os.listdir(tc_cache)
    dirs_to_rm = [os.path.join(tc_cache, x) for x in dirs_to_rm]
    dirs_to_rm = [x for x in dirs_to_rm if os.path.isdir(x)]

    num_dirs = len(dirs_to_rm)
    ui.info(ui.green, "Cleaning cache for", ui.blue, tc.name)
    if dry_run:
        print "Would remove %i packages" % num_dirs
        print "Use -f to proceed"
        return

    for (i, dir_to_rm) in enumerate(dirs_to_rm):
        sys.stdout.write("Removing package %i / %i\r" % ((i+1), num_dirs))
        sys.stdout.flush()
        qisys.sh.rm(dir_to_rm)
    ui.info(ui.green, "done")
