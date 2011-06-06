## Copyright (C) 2011 Aldebaran Robotics

""" Create a toolchain.
    This will create all necessary directories.
"""

import os
import logging
import ConfigParser

import qibuild
import qitoolchain

LOGGER = logging.getLogger("actions.qitoolchain.create")

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
    parser.add_argument("toolchain_name", metavar="NAME", action="store", help="the toolchain name")

def do(args):
    """ Main method """
    toolchain_name = args.toolchain_name
    qitoolchain.create(toolchain_name)
    toolchain = qitoolchain.Toolchain(toolchain_name)

    cfg_path = qitoolchain.get_tc_config_path()
    parser = ConfigParser.ConfigParser()
    parser.read(cfg_path)
    toolchain_section = 'toolchain "%s"' % toolchain_name
    if parser.has_section(toolchain_section):
        raise Exception("Toolchain %s already exists in configuration" % toolchain_name)

    qibuild.configstore.update_config(cfg_path,
        'toolchain "%s"' % toolchain_name, "path", toolchain.path)

