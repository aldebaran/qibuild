#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Test Project Config.
Automatic testing for qibuild.project.ProjectConfig.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import unittest
from io import StringIO

from qibuild.config import ProjectConfig


def cfg_from_string(input_str):
    """ Config From String """
    cfg_loc = StringIO(input_str)
    project_cfg = ProjectConfig()
    project_cfg.read(cfg_loc)
    return project_cfg


class ProjectConfigTestClass(unittest.TestCase):
    """ ProjectConfigTestClass """

    def test_simple_read(self):
        """ Test Simple Read """
        xml = """\n<project name="foo" />\n"""
        project_cfg = cfg_from_string(xml)
        self.assertEqual(project_cfg.name, "foo")

    def test_read_depends(self):
        """ Test Read Depends """
        xml = """
<project name="foo">
    <depends runtime="true" buildtime="true"
        names="bar baz"
    />
    <depends runtime="true"
        names="spam" />
    />
    <depends buildtime="true"
        names="eggs"
    />
    <depends testtime="true"
        names="gtest"
    />
</project>
"""
        project_cfg = cfg_from_string(xml)
        self.assertEqual(project_cfg.build_depends, set(["bar", "baz", "eggs"]))
        self.assertEqual(project_cfg.run_depends, set(["bar", "baz", "spam"]))
        self.assertEqual(project_cfg.test_depends, set(["gtest"]))


def test_write(tmpdir):
    """ Test Write """
    cfg = ProjectConfig()
    cfg.name = "foobar"
    cfg.build_depends = set(["foo", "bar"])
    cfg.run_depends = set(["foo"])
    cfg.test_depends = set(["foo", "bar", "gtest"])
    xml = tmpdir.join("project.xml")
    cfg.write(xml.strpath)
    cfg2 = ProjectConfig()
    cfg2.read(xml.strpath)
    assert cfg2 == cfg


if __name__ == "__main__":
    unittest.main()
