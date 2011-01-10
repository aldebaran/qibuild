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

import os
import logging
import ConfigParser

import qitools
import qitoolchain

LOGGER = logging.getLogger("actions.qitoolchain.create")

def configure_parser(parser):
    """Configure parser for this action """
    qitools.cmdparse.default_parser(parser)
    parser.add_argument("toolchain_name", action="store", help="the toolchain name")
    parser.add_argument("toolchain_feed", nargs='?', action="store", help="an url to a toolchain feed")

def do(args):
    """ Main method """
    toolchain_name = args.toolchain_name
    toolchain_feed = args.toolchain_feed
    qitoolchain.create(toolchain_name)
    toolchain = qitoolchain.Toolchain(toolchain_name, toolchain_feed)
    config_path = toolchain.config_path
    if not os.path.exists(config_path):
        qitools.sh.mkdir(os.path.dirname(config_path), recursive=True)

    parser = ConfigParser.ConfigParser()
    parser.read(toolchain.config_path)
    toolchain_section = 'toolchain "%s"' % toolchain_name
    if parser.has_section(toolchain_section):
        raise Exception("Toolchain %s already exists in configuration" % toolchain_name)

    # Create a new section for the new toolchain:
    parser.add_section(toolchain_section)
    if toolchain_feed:
        parser.set(toolchain_section, "feed", toolchain_feed)


    with open(toolchain.config_path, "w") as config_file:
        parser.write(config_file)

