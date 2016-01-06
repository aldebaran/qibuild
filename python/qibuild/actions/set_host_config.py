## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Set the configuration to be used when building host tools"""

import qisys.parsers
import qibuild.config

def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("name")

def do(args):
    """ Main entry point """
    name = args.name
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    qibuild_cfg.set_host_config(name)
    qibuild_cfg.write()
