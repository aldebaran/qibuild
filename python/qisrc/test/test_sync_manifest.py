# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.


import qisrc.sync
import qisrc.manifest
import qisrc.git
from qisrc.test.conftest import TestGitWorkTree
import qisys.sh

# allow the existing foo/bar/baz names
# pylint: disable=blacklisted-name
# pylint: disable=unused-variable


def test_stores_url_and_groups(git_worktree, git_server):
    git_server.create_group("mygroup", ["foo", "bar"])
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest(manifest_url, groups=["mygroup"])

    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    manifest = worktree_syncer.manifest
    assert manifest.url == manifest_url
    assert manifest.groups == ["mygroup"]


def test_stores_branches(git_worktree, git_server):
    git_server.switch_manifest_branch("devel")
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest(manifest_url, branch="devel")
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    manifest = worktree_syncer.manifest
    assert manifest.url == manifest_url
    assert manifest.branch == "devel"


def test_pull_manifest_changes_when_syncing(git_worktree, git_server):
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest(manifest_url)
    git_worktree.tmpdir.join(".qi", "manifests", "default", "manifest.xml")

    # Push a random file
    git_server.push_file("manifest.git", "a_file", "some contents\n")
    worktree_syncer.sync()
    a_file = git_worktree.tmpdir.join(".qi", "manifests", "default", "a_file")
    assert a_file.read() == "some contents\n"


def test_use_correct_manifest_branch(git_worktree, git_server):
    git_server.switch_manifest_branch("devel")
    # Push a random file to the 'devel' branch
    git_server.push_file("manifest.git", "a_file", "some contents\n", branch="devel")
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest(manifest_url, branch="devel")
    local_manifest = git_worktree.tmpdir.join(".qi", "manifests", "default")
    git = qisrc.git.Git(local_manifest.strpath)
    a_file = git_worktree.tmpdir.join(".qi", "manifests", "default", "a_file")
    assert a_file.read() == "some contents\n"


def test_new_repos(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest(manifest_url)
    assert git_worktree.get_git_project("foo")


def test_moving_repos_simple_case(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest(manifest_url)
    git_server.move_repo("foo.git", "lib/foo")
    git_worktree.sync()
    assert git_worktree.get_git_project("lib/foo")


def test_moving_repos_rename_fails(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest(manifest_url)
    git_server.move_repo("foo.git", "lib/foo")
    # create a file named "lib" to make the rename fail
    lib = git_worktree.tmpdir.join("lib")
    lib.write("")
    git_worktree.sync()
    assert not git_worktree.get_git_project("lib/foo")
    assert git_worktree.get_git_project("foo")
    lib.remove()
    git_worktree.sync()
    assert git_worktree.get_git_project("lib/foo")
    assert not git_worktree.get_git_project("foo")


def test_moving_repos_with_force(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest(manifest_url)
    git_server.move_repo("foo.git", "lib/foo")
    git_worktree.tmpdir.ensure("lib", "foo", dir=True)
    git_worktree.configure_manifest(manifest_url, force=True)
    assert git_worktree.get_git_project("lib/foo")
    assert not git_worktree.get_git_project("foo")


def test_removing_repos(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest(manifest_url)
    git_server.remove_repo("foo.git")
    git_worktree.sync()
    assert not git_worktree.get_git_project("foo")


def test_changing_manifest_groups(git_worktree, git_server):
    git_server.create_group("a_group", ["a", "b"])
    git_server.create_group("foo_group", ["bar", "baz"])
    git_server.create_repo("c")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest(manifest_url,
                                    groups=["a_group"])
    git_projects = git_worktree.git_projects
    assert len(git_projects) == 2
    git_worktree.configure_manifest(manifest_url,
                                    groups=None)
    git_projects = git_worktree.git_projects
    assert len(git_projects) == 5
    git_worktree.configure_manifest(manifest_url,
                                    groups=["a_group", "foo_group"])
    git_projects = git_worktree.git_projects
    assert len(git_projects) == 4


def test_add_on_empty(git_worktree, git_server):
    foo = git_worktree.tmpdir.join("foo")
    foo.ensure(dir=True)
    foo_git = qisrc.git.Git(foo.strpath)
    foo_git.init()
    git_server.create_repo("foo")
    git_worktree.configure_manifest(git_server.manifest_url)


def test_evil_nested(git_worktree, git_server):
    git_server.create_repo("foo/bar")
    git_worktree.configure_manifest(git_server.manifest_url)
    git_server.create_repo("foo")
    git_worktree.configure_manifest(git_server.manifest_url)
    assert len(git_worktree.git_projects) == 2


def test_moving_repos_sync_action(git_worktree, git_server, qisrc_action):
    git_server.create_repo("lib/foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest(manifest_url)
    git_server.move_repo("lib/foo.git", "lib/bar")
    qisrc_action("sync")
    git_worktree = TestGitWorkTree()
    assert not git_worktree.get_git_project("lib/foo")
    assert git_worktree.get_git_project("lib/bar")
    # Sync twice just to test that nothing happens
    qisrc_action("sync")


def test_rm_nested_repos_root(git_worktree, git_server, qisrc_action):
    foo = git_server.create_repo("foo")
    git_server.create_repo("foo/bar")
    git_server.create_repo("foo/lol")
    git_worktree.configure_manifest(git_server.manifest_url)
    qisys.sh.rm(foo.src)
    qisrc_action("sync")
    assert git_worktree.get_git_project("foo")
    assert git_worktree.get_git_project("foo/bar")
    assert git_worktree.get_git_project("foo/lol")


def test_all_repos(git_worktree, git_server):
    git_server.create_group("default", ["a.git", "b.git"])
    git_server.create_repo("c.git")
    git_worktree.configure_manifest(git_server.manifest_url, all_repos=True)
    assert len(git_worktree.git_projects) == 3
