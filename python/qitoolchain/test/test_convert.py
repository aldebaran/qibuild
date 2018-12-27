#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Convert Gentoo Package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qitoolchain.qipackage
from qitoolchain.binary_package import convert_to_qibuild


def test_convert_gentoo_package(tmpdir, toolchains):
    """ Convert Gentoo Package """
    this_dir = os.path.dirname(__file__)
    json_c_bz2_path = os.path.join(this_dir, "packages", "json-c-0.9.tbz2")
    json_c_bz2 = qitoolchain.binary_package.open_package(json_c_bz2_path)
    converted = convert_to_qibuild(
        json_c_bz2,
        package_metadata={"name": "json-c", "version": "0.9"},
        output_dir=tmpdir.strpath
    )
    tc_test = toolchains.create("test")
    package = qitoolchain.qipackage.from_archive(converted)
    assert package.name == "json-c"
    assert package.version == "0.9"
    package.path = tmpdir.strpath
    tc_test.add_package(package)
