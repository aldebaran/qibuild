#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Extract a binary toolchain package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qitoolchain.qipackage
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.default_parser(parser)
    parser.add_argument("package_path",
                        help="Path to the package to extract")
    parser.add_argument("-o", "--output", dest="output",
                        help="Where to extract the files (default: working directory")


def do(args):
    """ Main Entry Point """
    package_path = args.package_path
    output = args.output or os.getcwd()
    qipackage = None
    try:
        qipackage = qitoolchain.qipackage.from_archive(package_path)
    except Exception:
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
