## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
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

def do(args):
    """Main entry point

    """
    feed = args.feed
    tc_name = args.name
    if tc_name:
        toolchain = qitoolchain.get_toolchain(tc_name)
        if not feed:
            feed = toolchain.feed_url
            if not feed:
                mess  = "Could not find feed for toolchain %s\n" % tc_name
                mess += "Please check configuration or " \
                        "specifiy a feed on the command line\n"
                raise Exception(mess)
        toolchain.update(feed)
    else:
        tc_names = qitoolchain.get_tc_names()
        for i, tc_name in enumerate(tc_names, start=1):
            toolchain = qitoolchain.toolchain.Toolchain(tc_name)
            tc_feed = toolchain.feed_url
            if not tc_feed:
                ui.warning("No feed found for %s, skipping" % tc_name)
                continue
            ui.info(ui.green, "*", ui.reset, "(%i/%i)" % (i, len(tc_names)),
                    ui.green, "Updating", ui.blue, tc_name)
            toolchain.update(tc_feed)
