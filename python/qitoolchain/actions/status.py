
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
    config = qibuild.configstore.ConfigStore()
    config.read(qitoolchain.get_tc_config_path())
    for toolchain_name in config.get("toolchain", default=dict()).keys():
        toolchain = qitoolchain.Toolchain(toolchain_name)
        print toolchain
        print
