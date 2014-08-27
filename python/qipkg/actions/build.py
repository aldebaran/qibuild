## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Build all the projects of the given pml file
"""

import qisys.parsers
import qipkg.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)

def do(args):
    """Main entry point"""
    pml_builders = qipkg.parsers.get_pml_builders(args)
    for pml_builder in pml_builders:
        pml_builder.build()

