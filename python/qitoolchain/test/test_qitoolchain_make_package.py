#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiToolchain Make Package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.qixml
import qitoolchain.qipackage


def test_create_extract(qitoolchain_action, tmpdir):
    """ Test Create Extract """
    food = tmpdir.join("foo")
    food.ensure("include", "foo.h", file=True)
    food.ensure("lib", "libfoo.so", file=True)
    package_xml = food.join("package.xml")
    package_xml.write("""\n<package name="foo" version="0.1" target="linux64" />\n""")
    package_path = qitoolchain_action(
        "make-package",
        "--output", tmpdir.strpath,
        food.strpath
    )
    assert package_path == tmpdir.join("foo-linux64-0.1.zip").strpath
    dest = tmpdir.join("dest")
    extracted = qitoolchain_action(
        "extract-package",
        "--output", dest.strpath,
        package_path
    )
    package_xml = os.path.join(extracted, "package.xml")
    tree = qisys.qixml.read(package_xml)
    root = tree.getroot()
    package = qitoolchain.qipackage.from_xml(root)
    assert package.name == "foo"
    assert package.version == "0.1"
    assert package.target == "linux64"


def test_on_invalid_xml(qitoolchain_action, tmpdir):
    """ Test on Invalid Xml """
    package_xml = tmpdir.join("package.xml")
    package_xml.write("<foo/>")
    error = qitoolchain_action("make-package", tmpdir.strpath, raises=True)
    assert "Root element" in error
