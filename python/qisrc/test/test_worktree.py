## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for worktree

"""

import os
import tempfile
import unittest

import qibuild.sh
import qisrc.worktree

class WorktreeTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tmp-archive-test")

    def create_worktee(self, xml):
        """ Create a worktree for tests with .qi/worktree.xml
        containing the string passed as parameter

        """
        dot_qi = os.path.join(self.tmp, ".qi")
        qibuild.sh.mkdir(dot_qi)
        worktree_xml = os.path.join(dot_qi, "worktree.xml")
        with open(worktree_xml, "w") as fp:
            fp.write(xml)
        worktree = qisrc.worktree.open_worktree(self.tmp)
        return worktree

    def test_read_projects(self):
        xml = """
<worktree>
    <project src="core/naoqi" />
    <project src="lib/libqi" />
</worktree>
"""
        worktree = self.create_worktee(xml)
        p_srcs = [p.src for p in worktree.projects]
        self.assertEquals(p_srcs, ["core/naoqi", "lib/libqi"])

    def test_read_git_projects(self):
        xml = """
<worktree>
    <project src="lib/libqi" />
    <project src="foo/gui" />
    <project src="foo/lib" git_project="foo" />
    <project src="foo" />
</worktree>
"""
        qibuild.sh.mkdir(os.path.join(self.tmp, "lib/libqi/.git"), recursive=True)
        qibuild.sh.mkdir(os.path.join(self.tmp, "foo/.git"), recursive=True)
        worktree = self.create_worktee(xml)
        foo_lib = worktree.get_project("foo/lib")
        self.assertEquals(foo_lib.git_project.src, "foo")
        libqi = worktree.get_project("lib/libqi")
        self.assertEquals(libqi.git_project, libqi)
        g_srcs = [p.src for p in worktree.git_projects]
        self.assertEquals(g_srcs, ["foo", "lib/libqi"])


    def test_add_project(self):
        xml = "<worktree />"
        worktree = self.create_worktee(xml)
        worktree.add_project("foo")
        self.assertEquals(len(worktree.projects), 1)
        foo = worktree.get_project("foo")
        self.assertEquals(foo.src, "foo")

    def test_add_git_project(self):
        xml = "<worktree />"
        worktree = self.create_worktee(xml)
        worktree.add_project("foo")
        qibuild.sh.mkdir(
            os.path.join(self.tmp, "foo", ".git"),
            recursive=True)

        # Re-open worktre, check that foo is in git_projects
        worktree = qisrc.open_worktree(self.tmp)
        self.assertEquals(len(worktree.git_projects), 1)
        git_foo = worktree.get_project("foo")
        self.assertEquals(git_foo.src, "foo")


    def test_get_manifest_projects(self):
        xml = """
<worktree>
  <project src="manifest/default"
           manifest="true"
  />
  <project src="manifest/custom"
           manifest="true"
  />
  <project src="foo" />
</worktree>
"""
        worktree = self.create_worktee(xml)
        manifest_projects = worktree.get_manifest_projects()
        manifest_srcs = [p.src for p in manifest_projects]
        self.assertEquals(manifest_srcs, ["manifest/custom", "manifest/default"])

    def test_add_manifest_project(self):
        xml = """
<worktree>
    <project src="manifest/default" />
</worktree>
"""
        worktree = self.create_worktee(xml)
        manifest_projects = worktree.get_manifest_projects()
        manifest_srcs = [p.src for p in manifest_projects]
        self.assertEquals(manifest_srcs, list())

        # Set the manifest project
        worktree.set_manifest_project("manifest/default")
        manifest_projects = worktree.get_manifest_projects()
        manifest_srcs = [p.src for p in manifest_projects]
        self.assertEquals(manifest_srcs, ["manifest/default"])

        # Adding same proect twice should do nothing:
        worktree.set_manifest_project("manifest/default")
        manifest_srcs = [p.src for p in manifest_projects]
        self.assertEquals(manifest_srcs, ["manifest/default"])


    def tearDown(self):
        qibuild.sh.rm(self.tmp)

if __name__ == "__main__":
    unittest.main()
