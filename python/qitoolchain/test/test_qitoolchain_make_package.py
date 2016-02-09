## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.qixml
import qitoolchain.qipackage

def test_create_extract(qitoolchain_action, tmpdir):
    foo = tmpdir.join("foo")
    foo.ensure("include", "foo.h", file=True)
    foo.ensure("lib", "libfoo.so", file=True)
    package_xml = foo.join("package.xml")
    package_xml.write("""
<package name="foo" version="0.1" target="linux64" />
""")
    package_path = qitoolchain_action("make-package",
                                      "--output", tmpdir.strpath,
                                      foo.strpath)
    assert package_path == tmpdir.join("foo-linux64-0.1.zip").strpath
    dest = tmpdir.join("dest")
    extracted = qitoolchain_action("extract-package",
                                   "--output", dest.strpath,
                                    package_path)
    package_xml = os.path.join(extracted, "package.xml")
    tree = qisys.qixml.read(package_xml)
    root = tree.getroot()
    package = qitoolchain.qipackage.from_xml(root)
    assert package.name == "foo"
    assert package.version == "0.1"
    assert package.target == "linux64"

def test_on_invalid_xml(qitoolchain_action, tmpdir, record_messages):
    package_xml = tmpdir.join("package.xml")
    package_xml.write("<foo/>")
    rc = qitoolchain_action("make-package", tmpdir.strpath, retcode=True)
    assert rc != 0
    assert record_messages.find("Root element")
