##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

""" Create a toolchain.
    This will create all necessary directories.
"""

import logging

import qibuild
import qitoolchain

LOGGER = logging.getLogger("actions.qitoolchain.create")

def configure_parser(parser):
    """Configure parser for this action """
    qitools.argparsecommand.action_parser(parser)
    parser.add_argument("toolchain", action="store", help="the toolchain name")
    parser.add_argument("feed", nargs='?', action="store", help="an url to a toolchain feed")

def do(args):
    """ Main method """
    qitoolchain.create(args.toolchain)

if __name__ == "__main__" :
    import sys
    qitools.argparsecommand.sub_command_main(sys.modules[__name__])
