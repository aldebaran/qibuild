## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import tempfile
import unittest
from StringIO import StringIO

import pytest

import qisrc.sync
import qisrc.git
import qibuild.sh

from qisrc.test.test_git import create_git_repo
from qisrc.test.test_git import create_git_repo_with_submodules
from qisrc.test.test_git import create_broken_submodules
from qisrc.test.test_git import read_readme
from qisrc.test.test_git import push_file


# pylint: disable-msg=E1101
@pytest.mark.slow
class SyncTestCase(unittest.TestCase):
    def setUp(self):
        qibuild.command.CONFIG["quiet"] = True
        self.tmp = tempfile.mkdtemp(prefix="test-qisrc-sync")
        qibuild.sh.mkdir(self.tmp)

    def tearDown(self):
        qibuild.command.CONFIG["quiet"] = False
        qibuild.sh.rm(self.tmp)

    def test_local_manifest_sync(self):
        create_git_repo(self.tmp, "qi/libqi")
        worktree = qisrc.worktree.create(self.tmp)
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
        qisrc.sync.init_worktree(worktree, manifest)
        self.assertEqual(len(worktree.projects), 1)
        libqi = worktree.projects[0]
        self.assertEqual(libqi.path,
                         os.path.join(worktree.root, "lib/libqi"))

    def test_sync_two_remotes(self):
        create_git_repo(self.tmp, "a/a_project.git")
        create_git_repo(self.tmp, "b/b_project.git")
        remote_a = os.path.join(self.tmp, "srv", "a")
        remote_b = os.path.join(self.tmp, "srv", "b")
        xml = """
<manifest>
    <remote name="a" fetch="{remote_a}" />
    <remote name="b" fetch="{remote_b}" />
    <project name="a_project.git" remote="a" />
    <project name="b_project.git" remote="b" />
</manifest>
"""
        xml = xml.format(remote_a=remote_a, remote_b=remote_b)
        manifest = os.path.join(self.tmp, "manifest.xml")
        with open(manifest, "w") as fp:
            fp.write(xml)
        worktree = qisrc.worktree.create(self.tmp)
        qisrc.sync.init_worktree(worktree, manifest)

    def test_git_manifest_sync(self):
        create_git_repo(self.tmp, "qi/libqi")
        manifest_url = create_git_repo(self.tmp, "manifest.git")
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
        push_file(self.tmp, "manifest.git", "default.xml", xml)
        worktree = qisrc.worktree.create(self.tmp)
        fetched_manifest = qisrc.sync.fetch_manifest(worktree, manifest_url)
        with open(fetched_manifest, "r") as fp:
            fetched_xml = fp.read()
        self.assertEqual(fetched_xml, xml)
        qisrc.sync.init_worktree(worktree, fetched_manifest)
        # And do it a second time, checking that we don't get an
        # 'directory not empty' git failure
        qisrc.sync.init_worktree(worktree, fetched_manifest)

    def test_git_manifest_sync_branch(self):
        # Two branches in the manifest repo:
        #  - master:  3 projects: naoqi, libnaoqi and doc
        #  - release-1.12: 2 projects: naoqi and doc, but doc stays with the
        #   'master' branch
        manifest_url = create_git_repo(self.tmp, "manifest.git", with_release_branch=True)
        create_git_repo(self.tmp, "naoqi", with_release_branch=True)
        create_git_repo(self.tmp, "libnaoqi")
        create_git_repo(self.tmp, "doc")
        xml = """
<manifest>
    <remote name="origin" fetch="{tmp}/srv" />
    <project name="naoqi.git" path="naoqi" />
    <project name="libnaoqi.git" path="lib/libnaoqi" />
    <project name="doc" path="doc" />
</manifest>
"""
        xml = xml.format(tmp=self.tmp)
        push_file(self.tmp, "manifest.git", "default.xml", xml)

        xml = """
<manifest>
    <remote name="origin" fetch="{tmp}/srv" revision="release-1.12" />
    <project name="naoqi.git" path="naoqi" />
    <project name="doc" path="doc" revision="master" />
</manifest>
"""
        xml = xml.format(tmp=self.tmp)
        push_file(self.tmp, "manifest.git", "default.xml", xml, branch="release-1.12")

        master_root  = os.path.join(self.tmp, "work", "master")
        release_root = os.path.join(self.tmp, "work", "release-1.12")
        qibuild.sh.mkdir(master_root,  recursive=True)
        qibuild.sh.mkdir(release_root, recursive=True)
        master_wt  = qisrc.worktree.create(master_root)
        release_wt = qisrc.worktree.create(release_root)
        master_manifest  = qisrc.sync.fetch_manifest(master_wt,  manifest_url,
            branch="master")
        release_manifest = qisrc.sync.fetch_manifest(release_wt, manifest_url,
            branch="release-1.12")
        qisrc.sync.init_worktree(master_wt,  master_manifest)
        qisrc.sync.init_worktree(release_wt, release_manifest)
        release_srcs = [p.src for p in release_wt.projects]
        self.assertEqual(release_srcs, ["doc", "manifest/default", "naoqi"])
        naoqi_release = release_wt.get_project("naoqi")
        readme = read_readme(naoqi_release.path)
        self.assertEqual(readme, "naoqi on release-1.12\n")
        self.assertEqual(naoqi_release.remote, "origin")
        self.assertEqual(naoqi_release.branch, "release-1.12")

        master_srcs = [p.src for p in master_wt.projects]
        self.assertEqual(master_srcs, ["doc", "lib/libnaoqi", "manifest/default", "naoqi"])
        naoqi_master = master_wt.get_project("naoqi")
        readme = read_readme(naoqi_master.path)
        self.assertEqual(readme, "naoqi\n")
        self.assertEqual(naoqi_master.remote, "origin")
        self.assertEqual(naoqi_master.branch, "master")


    def test_manifest_wrong_revision(self):
        manifest_url = create_git_repo(self.tmp, "manifest", with_release_branch=True)
        xml = """
<manifest>
    <remote fetch="git@foo" name="origin" revision="release-1.12" />
</manifest>
"""
        push_file(self.tmp, "manifest", "default.xml", xml, branch="release-1.12")
        worktree = qisrc.worktree.create(self.tmp)
        qisrc.sync.clone_project(worktree, manifest_url)
        manifest = qisrc.sync.fetch_manifest(worktree, manifest_url, branch="release-1.12")
        qisrc.sync.init_worktree(worktree, manifest)
        worktree.set_manifest_project("manifest/default")
        manifest_projects = worktree.get_manifest_projects()
        self.assertEqual(len(manifest_projects), 1)
        manifest_path = manifest_projects[0].path
        readme = read_readme(manifest_path)
        self.assertEqual(readme, "manifest on release-1.12\n")


    def test_nested_git_projs(self):
        manifest_url = create_git_repo(self.tmp, "manifest")
        create_git_repo(self.tmp, "bar")
        create_git_repo(self.tmp, "foo")
        xml = """
<manifest>
    <remote name="origin" fetch="{tmp}/srv" />
    <project name="bar.git" path="bar" />
    <project name="foo.git" path="bar/foo"/>
</manifest>
"""
        xml = xml.format(tmp=self.tmp)
        push_file(self.tmp, "manifest", "default.xml", xml)

        worktree = qisrc.worktree.create(self.tmp)
        manifest = qisrc.sync.fetch_manifest(worktree, manifest_url)
        qisrc.sync.init_worktree(worktree, manifest)
        worktree.set_manifest_project("manifest/default")
        self.assertEqual(worktree.git_projects[0].src, "bar")
        self.assertEqual(worktree.git_projects[1].src, "bar/foo")

    def test_erasing_submodules_with_manifest_should_raise(self):
        manifest_url = create_git_repo(self.tmp, "manifest")
        create_git_repo_with_submodules(self.tmp)
        xml = """
<manifest>
    <remote name="origin" fetch="{tmp}/srv" />
    <project name="foo.git" path="foo" />
    <project name="bar.git" path="foo/bar"/>
</manifest>
"""
        xml = xml.format(tmp=self.tmp)
        push_file(self.tmp, "manifest", "default.xml", xml)
        work = os.path.join(self.tmp, "work")
        worktree = qisrc.worktree.create(work)
        manifest = qisrc.sync.fetch_manifest(worktree, manifest_url)
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            qisrc.sync.init_worktree(worktree, manifest)
        assert "path already exists" in str(e.value)

    def test_broken_submodules(self):
        manifest_url = create_git_repo(self.tmp, "manifest")
        create_broken_submodules(self.tmp)
        xml = """
<manifest>
    <remote name="origin" fetch="{tmp}/srv" />
    <project name="foo.git" path="foo" />
</manifest>
"""
        xml = xml.format(tmp=self.tmp)
        push_file(self.tmp, "manifest", "default.xml", xml)
        work = os.path.join(self.tmp, "work")
        worktree = qisrc.worktree.create(work)
        manifest = qisrc.sync.fetch_manifest(worktree, manifest_url)
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            qisrc.sync.init_worktree(worktree, manifest)
        assert "Broken submodules" in str(e.value)


if __name__ == "__main__":
    unittest.main()
