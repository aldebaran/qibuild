
##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""Display the toolchains status:
their names, and what projects they provide

"""

import qitools
import qitoolchain


def configure_parser(parser):
    """Configure parser for this action """
    qitools.cmdparse.default_parser(parser)


def do(args):
    """ Main method """
    config = qitools.configstore.ConfigStore()
    config.read(qitoolchain.get_config_path())
    for toolchain_name in config.get("toolchain").keys():
        print "Toolchain: ", toolchain_name
        toolchain = qitoolchain.Toolchain(toolchain_name)
        print "  feed:", toolchain.feed
        print "  packages: "
        for package in toolchain.packages:
            print " " * 4, package.name, "( deps:", " ".join(package.depends), ")"

