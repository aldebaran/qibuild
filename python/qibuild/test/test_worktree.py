## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for worktree

"""

import os
import tempfile
import unittest

import qibuild.sh
import qibuild.worktree

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
        worktree = qibuild.worktree.open_worktree(self.tmp)
        return worktree

    def test_read_projects(self):
        xml = """
<worktree>
    <project
        name="naoqi"
        src="core/naoqi"
    />
    <project
        name="libqi"
        src="lib/libqi"
    />
</worktree>
"""
        worktree = self.create_worktee(xml)
        project_names = [p.name for p in worktree.projects]
        self.assertEquals(project_names, ["libqi", "naoqi"])
        naoqi = worktree.get_project("naoqi")
        self.assertEquals(naoqi.src,
            os.path.join(self.tmp, "core/naoqi"))

    def test_read_git_projects(self):
        xml = """
<worktree>
    <project
        name="libqi"
        src="lib/libqi"
    />
    <project
        name="foo-gui"
        src="foo/gui"
    />
    <project
        name="foo-lib"
        src="foo/lib"
        git_project="foo"
    />
    <project
        name="foo"
        src="foo"
    />
</worktree>
"""
        qibuild.sh.mkdir(os.path.join(self.tmp,
            "lib/libqi/.git"), recursive=True)
        qibuild.sh.mkdir(os.path.join(self.tmp,
            "foo/.git"), recursive=True)
        worktree = self.create_worktee(xml)
        foo_lib = worktree.get_project("foo-lib")
        self.assertEquals(foo_lib.git_project.name, "foo")
        self.assertEquals(foo_lib.git_project.src,
            os.path.join(self.tmp, "foo"))
        libqi = worktree.get_project("libqi")
        self.assertEquals(libqi.git_project, libqi)
        g_names = [p.name for p in worktree.git_projects]
        self.assertEquals(g_names, ["foo", "libqi"])


    def test_add_project(self):
        xml = "<worktree />"
        worktree = self.create_worktee(xml)
        worktree.add_project("foo")
        self.assertEquals(len(worktree.projects), 1)
        foo = worktree.get_project("foo")
        self.assertEquals(foo.src,
            os.path.join(self.tmp, "foo"))

    def test_add_git_project(self):
        xml = "<worktree />"
        worktree = self.create_worktee(xml)
        worktree.add_project("foo")
        qibuild.sh.mkdir(
            os.path.join(self.tmp, "foo", ".git"),
            recursive=True)

        # Re-open worktre, check that foo is in git_projects
        worktree = qibuild.open_worktree(self.tmp)
        self.assertEquals(len(worktree.git_projects), 1)
        git_foo = worktree.get_project("foo")
        self.assertEquals(git_foo.src,
            os.path.join(self.tmp, "foo"))

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

if __name__ == "__main__":
    unittest.main()
