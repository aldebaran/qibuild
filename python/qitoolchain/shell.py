##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##  - Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

""" Collection of parser fonctions for qitoolchain
"""

def toolchain_parser(parser):
    """ Given a parser, add the options controling log
    """
    group = parser.add_argument_group("toolchain arguments")
    group.add_argument("toolchain", action="store", help="the toolchain name")
