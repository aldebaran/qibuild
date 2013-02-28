import pytest
import xml.etree.ElementTree as etree

import qisrc.groups

def test_parser():
    file = """
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

    root = etree.fromstring(file)

    groups = qisrc.groups.Groups()
    parser = qisrc.groups.GroupsParser(groups)
    parser.parse(root)

    assert groups.projects('c') == list()
    assert set(groups.projects('d')) - set(['bar', 'foo']) == set()
    assert set(groups.projects('a')) - set(['bar', 'foo', 'b', 'c', 'd']) == set()
