## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Launch automatic tests -- deprecated, use `qitest run` instead
"""

import sys

from qisys import ui
import qitest.actions.run

def configure_parser(parser):
    """Configure parser for this action"""
    qitest.actions.run.configure_parser(parser)
    parser.set_defaults(num_jobs=1)

def do(args):
    """Main entry point"""
    ui.warning("qibuild test is deprecated, use `qitest run` instead")
    qitest.actions.run.do(args)


