## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Display the toolchains names.

"""

import qibuild
import qitoolchain


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.default_parser(parser)


def do(args):
    """ Main method """
    tc_names = qitoolchain.get_tc_names()
    print "Known toolchains:"
    for tc_name in tc_names:
        print "  ", tc_name
    print
    print "Use ``qitoolchain info <tc_name>`` for more info"
