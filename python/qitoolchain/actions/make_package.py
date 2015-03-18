## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Create a package from a directory """

import os

from qisys import ui
from qisys.qixml import etree
import qisys.archive
import qisys.parsers

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    parser.add_argument("directory")
    parser.add_argument("-n", "--name", dest="name", required=True)
    parser.add_argument("--version", dest="version", required=True)
    parser.add_argument("--target")
    parser.add_argument("-o", "--output",
                        help="Base directory in which to create the archive. "
                             "Defaults to current working directory")

def do(args):
    input_directory = args.directory
    name = args.name
    version = args.version
    target = args.target
    output = args.output or os.getcwd()
    package_xml = os.path.join(args.directory, "package.xml")
    if not os.path.exists(package_xml):
        root = etree.Element("package")
        tree = etree.ElementTree(root)
    else:
        tree = qisys.qixml.read(package_xml)
        root = tree.getroot()
    root.set("name", name)
    root.set("version", version)
    if target:
        root.set("target", target)
    qisys.qixml.write(tree, package_xml)

    parts = [name]
    if target:
        parts.append(target)
    parts.append(version)
    archive_name = "-".join(parts) + ".zip"
    output = os.path.join(output, archive_name)
    res = qisys.archive.compress(input_directory, flat=True, output=output)
    ui.info(ui.green, "Package generated in", res)
    return res
