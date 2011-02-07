##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""Add a new package in a toolchain dir
"""

import logging

import qitools
import qitoolchain

LOGGER = logging.getLogger("actions.qitoolchain.add")


def configure_parser(parser):
    """Configure parser for this action """
    qitools.cmdparse.default_parser(parser)
    parser.add_argument("toolchain_name", action="store",
        help="name of the toolchain to add the project to.")
    parser.add_argument("package_path",
        help="the path of the package to add")

def do(args):
    """Retrieve the latest version from the server, if not already
    in cache

    Then, extract the package to the toolchains subdir
    """
    package_path = qitools.sh.to_native_path(args.package_path)
    toolchain = qitoolchain.Toolchain(args.toolchain_name)
    toolchain.add_local_package(package_path)



if __name__ == "__main__" :
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])
