## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qisrc.test.conftest import TestGitWorkTree

import qisrc.manifest

def test_check(qisrc_action, git_server):
    # Get a correct xml file from the server:
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    qisrc_action("init", manifest_url)

    # copy it to an other place, make a mistake, and run --check:
    srv_xml = git_server.src.join("manifest", "manifest.xml")
    manifest = qisrc.manifest.Manifest(srv_xml.strpath)
    editable_path = qisrc_action.tmpdir.join("manifest.xml")
    manifest.manifest_xml = editable_path.strpath
    manifest.add_repo("doestnotexists.git", "nowhere", ["origin"])
    manifest.dump()

    rc = qisrc_action("check-manifest", editable_path.strpath,
                      retcode=True)
    assert rc != 0
    # running qisrc sync should still work:
    qisrc_action("sync")

    # this time create a correct xml and re-run --check:
    git_server.create_repo("bar.git")
    manifest = qisrc.manifest.Manifest(srv_xml.strpath)
    editable_path = qisrc_action.tmpdir.join("manifest.xml")
    manifest.manifest_xml = editable_path.strpath
    manifest.dump()

    qisrc_action("check-manifest", editable_path.strpath)
    git_worktree = TestGitWorkTree()
    assert git_worktree.get_git_project("bar")

    # running qisrc sync just to be sure:
    qisrc_action("sync")

def test_check_configures_review(qisrc_action, git_server):

    # Get a correct xml file from the server:
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)

    git_server.create_repo("foo.git")
    git_server._create_repo("foo.git", review=True)

    # Create a foo repo, but without code review set
    foo_proj = qisrc_action.create_git_project("foo")
    assert not foo_proj.review

    # Edit the manifest.xml to set code review for foo
    srv_xml = git_server.src.join("manifest", "manifest.xml")
    manifest = qisrc.manifest.Manifest(srv_xml.strpath)
    editable_path = qisrc_action.tmpdir.join("manifest.xml")
    manifest.manifest_xml = editable_path.strpath

    foo_repo = manifest.get_repo("foo.git")
    foo_repo.remote_names = ["origin", "gerrit"]

    manifest.dump()

    # Run qisrc check-manifest
    qisrc_action("check-manifest", editable_path.strpath)

    # Code review should be now set:
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    assert foo_proj.review


def test_check_adding_group(qisrc_action, git_server):
    git_server.create_repo("a.git")
    git_server.create_group("default", ["b'.git"], default=True)
    qisrc_action("init", git_server.manifest_url)

    # Edit the manifest.xml to set code review for foo
    srv_xml = git_server.src.join("manifest", "manifest.xml")
    manifest = qisrc.manifest.Manifest(srv_xml.strpath)
    editable_path = qisrc_action.tmpdir.join("manifest.xml")
    manifest.manifest_xml = editable_path.strpath

    manifest.configure_group("foo", ["a.git"])

    qisrc_action("add-group", "foo")
    qisrc_action("check-manifest", editable_path.strpath)

    git_worktree = TestGitWorkTree()
    assert git_worktree.get_git_project("a")
