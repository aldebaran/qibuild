## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Update every toolchain using the feed that was used to create them

If a toolchain name is given, only update this toolchain.
If a feed url is given, use this feed instead of the recorded one
to update the given toolchain.
"""

from qisys import ui
import qisys.parsers
import qitoolchain

def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("name", nargs="?", metavar="NAME",
        help="Update only this toolchain")
    parser.add_argument("feed", metavar="TOOLCHAIN_FEED",
        help="Use this feed location to update the toolchain.\n",
        nargs="?")
    parser.add_argument("--dry-run", action="store_true",
        help="Print what would be done")

def do(args):
    """Main entry point

    """
    feed = args.feed
    tc_name = args.name
    dry_run = args.dry_run
    if tc_name:
        toolchain = qitoolchain.get_toolchain(tc_name)
        if not feed:
            feed = qitoolchain.toolchain.get_tc_feed(tc_name)
            if not feed:
                mess  = "Could not find feed for toolchain %s\n" % tc_name
                mess += "Pleas check configuration or specifiy a feed on the command line\n"
                raise Exception(mess)
        ui.info(ui.green, "Updating toolchain", tc_name, "with", feed)
        toolchain.parse_feed(feed, dry_run=dry_run)
    else:
        tc_names = qitoolchain.get_tc_names()
        for i, tc_name in enumerate(tc_names, start=1):
            tc_feed = qitoolchain.toolchain.get_tc_feed(tc_name)
            ui.info(ui.green, "*", ui.reset, "(%i/%i)" % (i, len(tc_names)),
                    ui.green, "Updating", ui.blue, tc_name)
            if not tc_feed:
                ui.warning("No feed found for %s, skipping" % tc_name)
                continue
            ui.info(ui.green, "Reading", tc_feed)
            toolchain = qitoolchain.Toolchain(tc_name)
            toolchain.parse_feed(tc_feed, dry_run=dry_run)
