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

import ConfigParser
import logging

import qibuild
import qitoolchain

LOGGER = logging.getLogger("actions.qitoolchain.create")

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("toolchain_name", action="store", help="the toolchain name")
    parser.add_argument("toolchain_feed", nargs='?', action="store", help="an url to a toolchain feed")

def do(args):
    """ Main method """
    toolchain_name = args.toolchain_name
    toolchain_feed = args.toolchain_feed
    toc = qibuild.toc.open(args.work_tree, args, use_env=True)
    qitoolchain.create(toolchain_name)
    # Update toc configuration:
    config_path = toc.user_config_path
    parser = ConfigParser.ConfigParser()
    parser.read(config_path)
    build_section = 'general "build"'
    toolchain_section = 'toolchain "%s"' % toolchain_name
    if parser.has_section(toolchain_section):
        raise Exception("Toolchain %s already exists in configuration" % toolchain_name)

    if not parser.has_section(build_section):
        parser.add_section(build_section)

    try:
        parser.get(build_section, "toolchain")
    except ConfigParser.NoOptionError:
        parser.set(build_section, "toolchain", toolchain_name)

    # Create a new section for the new toolchain:
    parser.add_section(toolchain_section)
    if toolchain_feed:
        parser.set(toolchain_section, "feed", toolchain_feed)

    with open(config_path, "w") as config_file:
        parser.write(config_file)






