## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" List the contents of a package """

import zipfile

from qisys import ui
import qisys.parsers

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    parser.add_argument("pkg_path")

def do(args):
    pkg_path = args.pkg_path
    archive = zipfile.ZipFile(pkg_path)
    for fileinfo in archive.infolist():
        ui.info(fileinfo.filename)
