
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
    config.read(qitoolchain.toolchain.get_config_path())
    print config

