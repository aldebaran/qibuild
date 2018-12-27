#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Convert a binary archive into a qiBuild package. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys
import qisys.parsers
from qisys import ui
from qitoolchain.convert import convert_package, convert_from_conan, conan_json_exists
from qitoolchain.conan import Conan


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("--name", required=True, help="The name of the package")
    parser.add_argument("--version", help="The name of the package")
    parser.add_argument("package_path", metavar='PACKAGE_PATH',
                        help="The path to the archive or conan directory to be converted")
    parser.add_argument("--batch", dest="interactive", action="store_false",
                        help="Do not prompt for cmake module edition")
    parser.add_argument("--conan", action="store_true",
                        help="Define if we work on a conan package")
    parser.add_argument("--conan-shared", dest="shared", action="store_true",
                        help="Set to get the shared version of the conan library")
    parser.add_argument("--conan-static", dest="static", action="store_true",
                        help="Set to get the static version of the conan library")
    parser.add_argument("--conan-channel", dest='channels', action='append',
                        help="conan channel of the conan packages to be converted, could be used multiple times")
    parser.set_defaults(interactive=True, version="0.0.1")


def do(args):
    """ Convert a binary archive into a qiBuild package. """
    name = args.name
    interactive = args.interactive
    package_path = args.package_path
    if args.conan:
        shared = None
        if args.shared or args.static:
            msg = "--conan-shared and --conan-static are mutualy exlusive, please remove one of them."
            assert args.shared != args.static, msg
        if args.shared is True:
            shared = True
        if args.static is True:
            shared = False
        conan = Conan(args.name, args.version, args.channels, shared)
        if not conan_json_exists(package_path):
            package_path = conan.create()
        ui.info("Converting Conan package", package_path, "into a qiBuild package")
        res = convert_from_conan(package_path, name, args.version)
    else:
        ui.info("Converting", package_path, "into a qiBuild package")
        res = convert_package(package_path, name, interactive=interactive)
    message = """Conversion succeeded.\n\nqiBuild package:\n  {0}\n
You can add this qiBuild package to a toolchain using:
  qitoolchain add-package -c <config name> {0}
  or
  qitoolchain add-package -t <toolchain name> {0}""".format(res)

    qisys.ui.info(message)
    return res
