## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisrc.license

def test_reads_license_from_qiproject(tmpdir):
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
    package_xml = tmpdir.join("package.xml")
    package_xml.write("""
<package name="foo" version="0.1">
  <license>LGPL</license>
</package>
""")
    license_ = qisrc.license.read_license(package_xml.strpath)
    assert license_ == "LGPL"

def write_license(tmpdir):
    qiproject_xml = tmpdir.join("qiproject.xml")
    qiproject_xml.write("<project>")
    qisrc.license.write_license(qiproject_xml.strpath, "BSD")
    assert qisrc.license.read_license(qiproject_xml.strpath) == "BSD"
    qisrc.license.write_license(qiproject_xml.strpath, "GPL")
    assert qisrc.license.read_license(qiproject_xml.strpath) == "GPL"
