# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import xml.etree.ElementTree as etree

import pytest

import qisrc.groups


def test_parser_read():
    default_file = """
<groups>
  <group name="a">
    <project name="b" />
    <project name="c" />
    <group name="d" />
  </group>
  <group name="d">
    <project name="foo" />
    <project name="bar" />
  </group>
</groups>
"""

    root = etree.fromstring(default_file)

    groups = qisrc.groups.Groups()
    parser = qisrc.groups.GroupsParser(groups)
    parser.parse(root)

    assert set(groups.projects('d')) - {'bar', 'foo'} == set()
    assert set(groups.projects('a')) - {'bar', 'foo', 'b', 'c', 'd'} == set()

    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.groups.GroupError):
        groups.projects("c")


def test_parser_write():
    groups = qisrc.groups.Groups()
    groups.configure_group("mygroup", ["a", "b"])

    parser = qisrc.groups.GroupsParser(groups)
    root = parser.xml_elem()
    groups = qisrc.groups.Groups()
    parser = qisrc.groups.GroupsParser(groups)
    parser.parse(root)
    assert groups.projects("mygroup") == ["a", "b"]
