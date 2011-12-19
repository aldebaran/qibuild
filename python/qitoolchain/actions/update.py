## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Update every toolchain using the feed that was used to create them

If a toolchain name is given, only update this toolchain.
If a feed url is given, use this feed instead of the recorded one
to update the given toolchain.
"""

import logging

import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
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

    known_tc_names = qitoolchain.toolchain.get_tc_names()
    if tc_name:
        if not tc_name in known_tc_names:
            mess  = "No such toolchain: '%s'\n" % tc_name
            mess += "Known toolchains are: %s" % known_tc_names
            raise Exception(mess)
        if not feed:
            feed = qitoolchain.toolchain.get_tc_feed(tc_name)
            if not feed:
                mess  = "Could not find feed for toolchain %s\n" % tc_name
                mess += "Pleas check configuration or specifiy a feed on the command line\n"
                raise Exception(mess)

        LOGGER.info("Updating toolchain %s using %s", tc_name, feed)
        toolchain = qitoolchain.Toolchain(tc_name)
        toolchain.parse_feed(feed, dry_run=dry_run)
    else:
        for tc_name in qitoolchain.get_tc_names():
            tc_feed = qitoolchain.toolchain.get_tc_feed(tc_name)
            if not tc_feed:
                LOGGER.info("No feed found for %s, skipping", tc_name)
                print
                continue
            LOGGER.info("###\n## Updating toolchain %s using %s\n##\n",
                tc_name, tc_feed)
            toolchain = qitoolchain.Toolchain(tc_name)
            toolchain.parse_feed(tc_feed, dry_run=dry_run)
            print

