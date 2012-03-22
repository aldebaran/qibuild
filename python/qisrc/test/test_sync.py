## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import tempfile
import unittest
from StringIO import StringIO

import qisrc.sync
import qisrc.git
import qibuild.sh


def create_git_repo(tmp, path):
    """ Create a empty git repository, which just
    what is enough so that it is possible to clone it

    Rerturn a valid git url
    """
    tmp_srv = os.path.join(tmp, "srv", path + ".git")
    qibuild.sh.mkdir(tmp_srv, recursive=True)
    srv_git = qisrc.git.Git(tmp_srv)
    srv_git.call("init", "--bare")

    tmp_src = os.path.join(tmp, "src", path)
    qibuild.sh.mkdir(tmp_src, recursive=True)
    readme = os.path.join(tmp_src, "README")
    with open(readme, "w") as fp:
        fp.write(path + "\n")
    git = qisrc.git.Git(tmp_src)
    git.call("init")
    git.call("add", ".")
    git.call("commit", "-m", "intial commit")
    git.call("push", tmp_srv, "master:master")

    return tmp_srv


class SyncTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-qisrc-sync")
        qibuild.sh.mkdir(self.tmp)

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_local_manifest_sync(self):
        create_git_repo(self.tmp, "qi/libqi")
        worktree = qibuild.worktree.create(self.tmp)
        xml = """
<manifest>
    <remote name="origin"
        fetch="{tmp}"
    />

    <project name="srv/qi/libqi.git"
        path="lib/libqi"
    />
</manifest>
"""
        xml = xml.format(tmp=self.tmp)
        manifest = StringIO(xml)
        qisrc.sync.sync_worktree(worktree, manifest)
        self.assertEqual(len(worktree.projects), 1)
        libqi = worktree.projects[0]
        self.assertEqual(libqi.src,
                         os.path.join(worktree.root, "lib/libqi"))

    def test_git_manifest_sync(self):
        create_git_repo(self.tmp, "qi/libqi")
        manifest_url = create_git_repo(self.tmp, "manifest")
        manifest_src = os.path.join(self.tmp, "src", "manifest")
        default_xml = os.path.join(manifest_src, "default.xml")
        xml = """
<manifest>
    <remote name="origin"
        fetch="{tmp}/srv"
    />

    <project name="qi/libqi.git"
        path="lib/libqi"
    />
</manifest>
"""
        xml = xml.format(tmp=self.tmp)
        with open(default_xml, "w") as fp:
            fp.write(xml)
        git = qisrc.git.Git(manifest_src)
        git.call("add", "default.xml")
        git.call("commit", "-m", "added default.xml")
        git.call("push", manifest_url, "master:master")
        other = os.path.join(self.tmp, "other")
        worktree = qibuild.worktree.create(other)
        qisrc.sync.sync_worktree_from_git(worktree, manifest_url)


if __name__ == "__main__":
    unittest.main()
