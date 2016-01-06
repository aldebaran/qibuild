## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Extract a binary toolchain package """

import os

from qisys import ui
import qisys.parsers
import qitoolchain.qipackage

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    parser.add_argument("package_path",
                        help="Path to the package to extract")
    parser.add_argument("-o", "--output", dest="output",
                        help="Where to extract the files (default: working directory")

def do(args):
    package_path = args.package_path
    output = args.output or os.getcwd()
    qipackage = None
    try:
        qipackage = qitoolchain.qipackage.from_archive(package_path)
    except:
        pass
    res = None
    if qipackage:
        name = qipackage.name
        if qipackage.target:
            name += "-" + qipackage.target
        if qipackage.version:
            name += "-" + qipackage.version
        dest = os.path.join(output, name)
        res = qitoolchain.qipackage.extract(package_path, dest)
    else:
        res = qisys.archive.extract(package_path, output)
    ui.info(ui.green, "Package extracted to", ui.reset, ui.bold, res)
    return res
