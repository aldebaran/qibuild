#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.license


def test_reads_license_from_qiproject(tmpdir):
    """ Test Read Licence """
    qiproject_xml = tmpdir.join("qiproject.xml")
    qiproject_xml.write("""
<project version="3">
  <maintainer email="jdoe@example.com">John Doe</maintainer>
  <license>BSD</license>
</project>
""")
    license_ = qisrc.license.read_license(qiproject_xml.strpath)
    assert license_ == "BSD"


def test_warns_when_no_license(tmpdir, record_messages):
    """ Test Warn When No Licence """
    qiproject_xml = tmpdir.join("qiproject.xml")
    qiproject_xml.write("""
<project version="3">
  <maintainer email="jdoe@example.com">John Doe</maintainer>
</project>
""")
    license_ = qisrc.license.read_license(qiproject_xml.strpath)
    assert license_ is None
    assert record_messages.find("does not define")


def test_reads_license_from_package(tmpdir):
    """ Test Read Licence From Package """
    package_xml = tmpdir.join("package.xml")
    package_xml.write("""
<package name="foo" version="0.1">
  <license>LGPL</license>
</package>
""")
    license_ = qisrc.license.read_license(package_xml.strpath)
    assert license_ == "LGPL"


def write_license(tmpdir):
    """ Write Licence """
    qiproject_xml = tmpdir.join("qiproject.xml")
    qiproject_xml.write("<project>")
    qisrc.license.write_license(qiproject_xml.strpath, "BSD")
    assert qisrc.license.read_license(qiproject_xml.strpath) == "BSD"
    qisrc.license.write_license(qiproject_xml.strpath, "GPL")
    assert qisrc.license.read_license(qiproject_xml.strpath) == "GPL"
