
## Copyright (C) 2011 Aldebaran Robotics

"""Display the toolchains status:
their names, and what projects they provide

"""

import qibuild
import qitoolchain


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)


def do(args):
    """ Main method """
    tc_names = qitoolchain.get_tc_names()
    for tc_name in tc_names:
        toolchain = qitoolchain.Toolchain(tc_name)
        print toolchain
        print
