#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Convert a Package to QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.sh

from qibuild.cmake.modules import add_cmake_module_to_archive
from qitoolchain.binary_package import convert_to_qibuild, open_package


def convert_package(package_path, name, interactive=False):
    """ Convert Package """
    dest_dir = os.path.dirname(package_path)
    package = open_package(package_path)
    with qisys.sh.TempDir() as tmp:
        qibuild_package_path = convert_to_qibuild(package, output_dir=tmp)
        add_cmake_module_to_archive(qibuild_package_path, name, interactive=interactive)
        src = os.path.abspath(qibuild_package_path)
        dst = os.path.join(dest_dir, os.path.basename(qibuild_package_path))
        dst = os.path.abspath(dst)
        qisys.sh.mv(src, dst)
        qibuild_package_path = dst
    return qibuild_package_path
