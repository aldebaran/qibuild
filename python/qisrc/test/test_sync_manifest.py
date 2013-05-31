## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


import qisrc.sync
import qisrc.manifest
import qisrc.git


def test_stores_url_and_groups(git_worktree, git_server):
    git_server.create_group("mygroup", ["foo", "bar"])
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest("default", manifest_url, groups=["mygroup"])

    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    manifests = worktree_syncer.manifests
    assert len(manifests) == 1
    default_manifest = manifests["default"]
    assert default_manifest.name == "default"
    assert default_manifest.url == manifest_url
    assert default_manifest.groups == ["mygroup"]

def test_stores_branches(git_worktree, git_server):
    git_server.switch_manifest_branch("devel")
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest("default", manifest_url, branch="devel")
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    manifests = worktree_syncer.manifests
    assert len(manifests) == 1
    default_manifest = manifests["default"]
    assert default_manifest.name == "default"
    assert default_manifest.url == manifest_url
    assert default_manifest.branch == "devel"

def test_pull_manifest_changes_when_syncing(git_worktree, git_server):
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest("default", manifest_url)
    git_worktree.tmpdir.join(".qi", "manifests", "default", "manifest.xml")

    # Push a random file
    git_server.push_file("manifest.git", "a_file", "some contents\n")
    worktree_syncer.sync()
    a_file = git_worktree.tmpdir.join(".qi", "manifests",
                                      "default", "a_file")
    assert a_file.read() == "some contents\n"

def test_use_correct_manifest_branch(git_worktree, git_server):
    git_server.switch_manifest_branch("devel")
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest("default", manifest_url, branch="devel")
    local_manifest = git_worktree.tmpdir.join(".qi", "manifests", "default")
    git = qisrc.git.Git(local_manifest.strpath)
    assert git.get_current_branch() == "devel"

def test_new_repos(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest("default", manifest_url)
    assert git_worktree.get_git_project("foo")

def test_moving_repos_simple_case(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest("default", manifest_url)
    git_server.move_repo("foo.git", "lib/foo")
    git_worktree.sync()
    assert git_worktree.get_git_project("lib/foo")

def test_moving_repos_rename_fails(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest("default", manifest_url)
    git_server.move_repo("foo.git", "lib/foo")
    # create a file named "lib" to make the rename fail
    lib = git_worktree.tmpdir.join("lib")
    lib.write("")
    git_worktree.sync()
    assert not git_worktree.get_git_project("lib/foo")
    assert git_worktree.get_git_project("foo")
    lib.remove()
    git_worktree.sync()
    assert  git_worktree.get_git_project("lib/foo")
    assert not git_worktree.get_git_project("foo")

def test_removing_repos(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest("default", manifest_url)
    git_server.remove_repo("foo.git")
    git_worktree.sync()
    assert not git_worktree.get_git_project("foo")


def test_changing_manifest_groups(git_worktree, git_server):
    git_server.create_group("a_group", ["a", "b"])
    git_server.create_group("foo_group", ["bar", "baz"])
    git_server.create_repo("c")
    manifest_url = git_server.manifest_url
    git_worktree.configure_manifest("default", manifest_url,
                                     groups=["a_group"])
    git_projects = git_worktree.git_projects
    assert len(git_projects) == 2
    git_worktree.configure_manifest("default", manifest_url,
                                    groups=list())
    git_projects = git_worktree.git_projects
    assert len(git_projects) == 5
    git_worktree.configure_manifest("default", manifest_url,
                                    groups=["a_group", "foo_group"])
    git_projects = git_worktree.git_projects
    assert len(git_projects) == 4
