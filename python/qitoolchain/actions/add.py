##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""Add a new package in a toolchain dir
"""

import os
import posixpath
import logging

import qitools
import qibuild
import qitoolchain

LOGGER = logging.getLogger("actions.qitoolchain.add")


def configure_parser(parser):
    """Configure parser for this action """
    qitoolchain.shell.toolchain_parser(parser)
    parser.add_argument("toolchain", action="store", help="the toolchain name")

def do(args):
    """Retrieve the latest version from the server, if not already
    in cache

    Then, extract the package to the toolchains subdir
    """


if __name__ == "__main__" :
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])
