## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Convert a binary archive into a qiBuild package.

"""

import os

import qisys
import qisys.parsers
from qitoolchain.convert import convert_package

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("--name", required=True,
                        help="The name of the package")
    parser.add_argument("package_path", metavar='PACKAGE_PATH',
                        help="The path to the archive to be converted")


def do(args):
    """Convert a binary archive into a qiBuild package.

    """
    name = args.name
    package_path = args.package_path
    ui.info("Converting", package_path, "into a qiBuild package")
    res = convert_package(package_path, name, interactive=True)
    message = """\
Conversion succeeded.

qiBuild package:
  {1}

You can add this qiBuild package to a toolchain using:
  qitoolchain add-package -c <toolchain name> {0} {1}\
""".format(name, res)
    qisys.ui.info(message)
