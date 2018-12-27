#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Create a package from a directory """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.archive
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.default_parser(parser)
    parser.add_argument("directory")
    parser.add_argument("-o", "--output",
                        help="Base directory in which to create the archive. "
                             "Defaults to current working directory")


def do(args):
    """ Main Entry Point """
    input_directory = args.directory
    output = args.output or os.getcwd()
    package_xml = os.path.join(args.directory, "package.xml")
    if not os.path.exists(package_xml):
        raise Exception("Expecting a package.xml at the root of the package")
    tree = qisys.qixml.read(package_xml)
    root = tree.getroot()
    if root.tag != "package":
        raise Exception("Root element should have a 'package' tag")
    name = qisys.qixml.parse_required_attr(root, "name")
    version = qisys.qixml.parse_required_attr(root, "version")
    target = qisys.qixml.parse_required_attr(root, "target")
    parts = [name, target, version]
    archive_name = "-".join(parts) + ".zip"
    output = os.path.join(output, archive_name)
    res = qisys.archive.compress(input_directory, flat=True, output=output)
    ui.info(ui.green, "Package generated in", res)
    return res
