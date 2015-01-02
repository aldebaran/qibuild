## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qipkg.manifest

def test_bump_version_explicit(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write('<package uuid="foo" version="0.0.3" />')
    qipkg.manifest.bump_version(manifest_xml.strpath, "0.2.0")
    expected = '<package uuid="foo" version="0.2.0" />'
    actual = manifest_xml.read()
    assert actual == expected

def test_bump_version_implicit(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write('<package uuid="foo" version="0.0.3" />')
    qipkg.manifest.bump_version(manifest_xml.strpath)
    expected = '<package uuid="foo" version="0.0.4" />'
    actual = manifest_xml.read()
    assert actual == expected

