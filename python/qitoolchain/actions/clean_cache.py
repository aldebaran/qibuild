## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Clean a toolchain cache """

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
    tc.clean_cache(dry_run=dry_run)
