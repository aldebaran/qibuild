
## Copyright (C) 2011 Aldebaran Robotics

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
    config.read(qitoolchain.get_tc_config_path())
    for toolchain_name in config.get("toolchain", default=dict()).keys():
        toolchain = qitoolchain.Toolchain(toolchain_name)
        print toolchain
