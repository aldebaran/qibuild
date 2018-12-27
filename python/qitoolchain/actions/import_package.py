#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Convert a binary archive into a qiBuild package and add it to a toolchain. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qitoolchain
import qitoolchain.parsers
import qitoolchain.qipackage
from qitoolchain.convert import convert_package
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qitoolchain.parsers.toolchain_parser(parser)
    parser.add_argument("--name", required=True,
                        help="The name of the package")
    parser.add_argument("package_path", metavar='PACKAGE_PATH',
                        help="The path to the package to be converted")
    parser.add_argument("-d", "--directory", dest="dest_dir",
                        metavar='DESTDIR', help="""\
destination directory of the qiBuild package after conversion
(default: aside the original package)""")
    parser.add_argument("--batch", dest="interactive", action="store_false",
                        help="Do not prompt for cmake module edition")
    parser.set_defaults(interactive=True)


def do(args):
    """
    Import a binary package into a toolchain
    - Convert the binary package into a qiBuild package
    - Add the qiBuild package to the cache
    - Add the qiBuild package from cache to toolchain
    """
    name = args.name
    package_path = args.package_path
    converted_package_path = convert_package(package_path, name,
                                             interactive=args.interactive)
    toolchain = qitoolchain.parsers.get_toolchain(args)
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(toolchain.name)
    message = """\nImporting '{1}' in the toolchain {0} ...\n""".format(toolchain.name, package_path)
    qisys.ui.info(message)
    # installation of the qiBuild package
    package_dest = os.path.join(tc_packages_path, name)
    qisys.sh.rm(package_dest)
    with qisys.sh.TempDir() as tmp:
        extracted = qisys.archive.extract(converted_package_path, tmp, quiet=True,
                                          strict_mode=False)
        qisys.sh.install(extracted, package_dest, quiet=True)
    qibuild_package = qitoolchain.qipackage.QiPackage(name, path=package_dest)
    toolchain.add_package(qibuild_package)
    ui.info("done")
