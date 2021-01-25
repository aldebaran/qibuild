#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Create a package from a directory """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import qisys.archive
import qisys.parsers
from qisys import ui
from qitoolchain.convert import add_package_xml
from qibuild.cmake.modules import generate_cmake_module, edit_module


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.default_parser(parser)
    parser.add_argument("directory")
    parser.add_argument("-o", "--output",
                        help="Base directory in which to create the archive. "
                             "Defaults to current working directory")
    parser.add_argument("--name", help="Name of the toolchain package")
    parser.add_argument("--version", help="Version of the toolchain package")
    parser.add_argument("--target", help="Target of the toolchain package")
    parser.add_argument("--license", help="License of the toolchain package")
    parser.add_argument("--auto", dest="auto", action="store_true",
                        help="Do not prompt for cmake module edition")
    parser.add_argument("--shared-only", dest="shared", action="store_true",
                        help="Only register shared lib in the cmake config file")
    parser.add_argument("--static-only", dest="static", action="store_true",
                        help="Only register static lib in the cmake config file")


def do(args):
    """ Main Entry Point """
    input_directory = args.directory
    output = args.output or os.getcwd()
    package_xml = os.path.join(args.directory, "package.xml")
    if not os.path.exists(package_xml) and not args.name:
        raise Exception("Expecting a package.xml at the root of the package")
    if args.name:
        if not args.version:
            raise Exception("A version must be specified if name present")
        else:
            add_package_xml(args.directory, args.name, args.version, args.target, args.license)
    tree = qisys.qixml.read(package_xml)
    root = tree.getroot()
    if root.tag != "package":
        raise Exception("Root element should have a 'package' tag")
    name = qisys.qixml.parse_required_attr(root, "name")
    version = qisys.qixml.parse_required_attr(root, "version")
    target = qisys.qixml.parse_required_attr(root, "target")
    package_cmake = os.path.join(args.directory, "share", "cmake", name.lower(), "{}-config.cmake".format(name.lower()))
    ui.debug("with package_cmake:", package_cmake)
    if not os.path.exists(package_cmake):
        ui.warning("Generating {}".format(package_cmake))
        if args.shared:
            exclude_ext = ".a"
        elif args.static:
            exclude_ext = ".so .dylib .dll"
        else:
            exclude_ext = None
        module = generate_cmake_module(args.directory, name, exclude_ext=exclude_ext)
        if not args.auto:
            edit_module(module)
    parts = [name, version, target]
    archive_name = "-".join(parts) + ".zip"
    output = os.path.join(output, archive_name)
    res = qisys.archive.compress(input_directory, flat=True, output=output)
    ui.info(ui.green, "Package generated in", res)
    return res
