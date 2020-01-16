#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Add a new package to a toolchain """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import zipfile
import argparse
import six

import qitoolchain.parsers
import qisys.archive
import qisys.remote
import qisys.worktree
from qisys import ui

if six.PY3:
    from urllib import parse as urlparse
else:
    import urlparse


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qitoolchain.parsers.toolchain_parser(parser)
    parser.add_argument("package_path", metavar='PATH', help="The path to the package")
    parser.add_argument("--name", help=argparse.SUPPRESS)


def do(args):
    """
    Add a package to a toolchain
    - Check that there is a current toolchain
    - Add the package to the cache
    - Add the package from cache to toolchain
    """
    toolchain = qitoolchain.parsers.get_toolchain(args)
    package_path = args.package_path
    legacy = False
    try:
        if not os.path.isfile(package_path) and \
           urlparse.urlparse(package_path).scheme:
            package_path = qisys.remote.download(package_path, ".")
        archive = zipfile.ZipFile(package_path, allowZip64=True)
        archive.read("package.xml")
    except KeyError:
        legacy = True
    if legacy and not args.name:
        raise Exception("Must specify --name when using legacy format")
    if args.name and not legacy:
        ui.warning("--name ignored when using modern format")
    package = None
    if legacy:
        package = qitoolchain.qipackage.QiPackage(args.name)
    else:
        package = qitoolchain.qipackage.from_archive(package_path)
    # extract it to the default packages path of the toolchain
    tc_name = toolchain.name
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc_name)
    dest = os.path.join(tc_packages_path, package.name)
    qisys.sh.rm(dest)
    qitoolchain.qipackage.extract(package_path, dest)
    package.path = dest
    # add the package to the toolchain
    toolchain.add_package(package)
