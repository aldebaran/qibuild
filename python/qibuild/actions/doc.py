## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Alias for qidoc.actions.build

"""

import qibuild
import qidoc.actions.build

def configure_parser(parser):
    """ Configure parser for this action """
    qidoc.actions.build.configure_parser(parser)

def do(args):
    """ Main entry point """
    qidoc.actions.build.do(args)

