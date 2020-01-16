#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Display status of subversion packages in the given toolchain """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys

import qisrc.svn
import qitoolchain
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("name", help="Name of the toolchain")


def do(args):
    """ Main entry point """
    toolchain = qitoolchain.get_toolchain(args.name)
    svn_packages = list()
    for package in toolchain.packages:
        svn_dir = os.path.join(package.path, ".svn")
        if os.path.exists(svn_dir):
            svn_packages.append(package)
    not_clean = list()
    for i, svn_package in enumerate(svn_packages, start=1):
        to_write = "Checking (%d/%d) " % (i, len(svn_packages))
        sys.stdout.write(to_write + "\r")
        sys.stdout.flush()
        svn = qisrc.svn.Svn(svn_package.path)
        _rc, out = svn.call("status", raises=False)
        if out:
            not_clean.append((svn_package.name, out))
    if not not_clean:
        ui.info("\n", ui.green, "All OK")
        sys.exit(0)
    ui.warning("Some svn packages are not clean")
    for name, message in not_clean:
        ui.info(ui.green, "*", ui.reset, ui.blue, name)
        ui.info(message)
    sys.exit(1)
