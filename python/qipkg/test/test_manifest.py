#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qipkg.manifest


def test_bump_version_explicit(tmpdir):
    """ Test Bump Version Explicit """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write('<package uuid="foo" version="0.0.3" />')
    qipkg.manifest.bump_version(manifest_xml.strpath, "0.2.0")
    expected = '<package uuid="foo" version="0.2.0" />'
    actual = manifest_xml.read()
    assert actual == expected


def test_bump_version_implicit(tmpdir):
    """ Test Bump Version Implicit """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write('<package uuid="foo" version="0.0.3" />')
    qipkg.manifest.bump_version(manifest_xml.strpath)
    expected = '<package uuid="foo" version="0.0.4" />'
    actual = manifest_xml.read()
    assert actual == expected
