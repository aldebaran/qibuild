## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Alias for `qisrc create`

"""

from qisys import ui
import qisrc.actions.create


def configure_parser(parser):
    """ Configure parser for this action """
    qisrc.actions.create.configure_parser(parser)

def do(args):
    """ Main entry point """
    ui.warning("`qibuild create` is deprecated in qibuild2, use"
               "`qisrc create` instead")
    qisrc.actions.create.do(args)

