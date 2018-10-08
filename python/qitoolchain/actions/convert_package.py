#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Convert a binary archive into a qiBuild package. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys
import qisys.parsers
from qisys import ui
from qitoolchain.convert import convert_package


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("--name", required=True, help="The name of the package")
    parser.add_argument("package_path", metavar='PACKAGE_PATH',
                        help="The path to the archive to be converted")
    parser.add_argument("--batch", dest="interactive", action="store_false",
                        help="Do not prompt for cmake module edition")
    parser.set_defaults(interactive=True)


def do(args):
    """ Convert a binary archive into a qiBuild package. """
    name = args.name
    interactive = args.interactive
    package_path = args.package_path
    ui.info("Converting", package_path, "into a qiBuild package")
    res = convert_package(package_path, name, interactive=interactive)
    message = """Conversion succeeded.\n\nqiBuild package:\n  {0}\n
You can add this qiBuild package to a toolchain using:
  qitoolchain add-package -c <toolchain name> {0}""".format(res)
    qisys.ui.info(message)
    return res
