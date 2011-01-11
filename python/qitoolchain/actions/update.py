##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

""" Update a toolchain
    This will try to update every package already found in the toolchain
"""

import qitools
import qitoolchain

def configure_parser(parser):
    """Configure parser for this action """
    qitools.cmdparse.default_parser(parser)
    parser.add_argument("toolchain_name", metavar="NAME", action="store", help="the toolchain name")
    parser.add_argument("toolchain_feed", nargs='?', metavar="FEED", action="store",
        help="an url to a toolchain feed. If not given, the previous feed will be used. "
             "Warning ! No backup is made if you change the toolchain feed")


def do(args):
    """Main method """
    toolchain_name = args.toolchain_name
    toolchain_feed = args.toolchain_feed
    toolchain = qitoolchain.Toolchain(toolchain_name)
    toolchain.update(toolchain_feed)

