## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Automatic testing for qibuild.project.ProjectConfig

"""

import os
import qibuild
import unittest
from StringIO import StringIO

def cfg_from_string(str, user_config=None):
    cfg_loc = StringIO(str)
    project_cfg = qibuild.config.ProjectConfig()
    project_cfg.read(cfg_loc)
    return project_cfg

class ProjectConfigTestClass(unittest.TestCase):

    def test_simple_read(self):
        xml = """
<project name="foo" />
"""
        project_cfg = cfg_from_string(xml)
        self.assertEqual(project_cfg.name, "foo")

    def test_read_depends(self):
        xml = """
<project name="foo">
    <depends name="bar" />
    <depends name="baz" />
    <rdepends name="spam" />
</project>
"""
        project_cfg = cfg_from_string(xml)
        self.assertEqual(project_cfg.depends, ["bar", "baz"])
        self.assertEqual(project_cfg.rdepends, ["spam"])


if __name__ == "__main__":
    unittest.main()



