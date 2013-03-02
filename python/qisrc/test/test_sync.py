## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


import qisrc.sync
import qisrc.manifest

def make_repos(*args):
    res = list()
    for (project, src) in args:
        repo = qisrc.manifest.RepoConfig()
        repo.remote_url = "git://src/" + project
        repo.project = project
        repo.src = src
        res.append(repo)
    return res

def test_compute_no_diff():
    old = make_repos(
        ("foo.git", "foo"),
        ("bar.git", "bar")
    )
    new = make_repos(
        ("foo.git", "foo"),
        ("bar.git", "bar")
    )
    (to_add, to_move, to_rm) = qisrc.sync.compute_repo_diff(old, new)
    assert to_add == list()
    assert to_move == list()
    assert to_rm == list()

def test_compute_moves():
    old = make_repos(
        ("foo.git", "foo"),
        ("bar.git", "bar")
    )
    new = make_repos(
        ("bar.git", "bar"),
        ("foo.git", "lib/foo"),
    )
    (to_add, to_move, to_rm) = qisrc.sync.compute_repo_diff(old, new)
    assert to_add == list()
    assert len(to_move) == 1
    assert to_move[0][0].project == "foo.git"
    assert to_move[0][1] == "lib/foo"
    assert to_rm == list()

def test_compute_rm_add():
    old = make_repos(
        ("foo.git", "foo"),
        ("bar.git", "bar"),
    )
    new = make_repos(
        ("foo.git", "foo"),
        ("spam.git", "spam"),
    )
    (to_add, to_move, to_rm) = qisrc.sync.compute_repo_diff(old, new)
    assert len(to_add) == 1
    assert to_add[0].project == "spam.git"
    assert to_move == list()
    assert len(to_rm) == 1
    assert to_rm[0].project == "bar.git"



def test_stores_url_and_groups(git_worktree, git_server):
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.add_manifest("default", manifest_url, groups=["qim"])

    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    manifests = worktree_syncer.manifests
    assert len(manifests) == 1
    default_manifest = manifests["default"]
    assert default_manifest.name == "default"
    assert default_manifest.url == manifest_url
    assert default_manifest.groups == ["qim"]

def test_updates_manifests_when_loading(git_worktree, git_server):
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.add_manifest("default", manifest_url)
    git_worktree.tmpdir.join(".qi", "manifests", "default", "manifest.xml")

    # Push a random file
    git_server.push_file("manifest.git", "a_file", "some contents\n")
    worktree_syncer.load_manifests()
    a_file = git_worktree.tmpdir.join(".qi", "manifests",
                                      "default", "a_file")
    assert a_file.read() == "some contents\n"


def test_new_repos(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.add_manifest("default", manifest_url)
    assert git_worktree.get_git_project("foo")

def test_moving_repos_simple_case(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.add_manifest("default", manifest_url)
    git_server.move_repo("foo.git", "lib/foo")
    git_worktree.sync()
    assert git_worktree.get_git_project("lib/foo")

def test_moving_repos_rename_fails(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.add_manifest("default", manifest_url)
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
    git_worktree.add_manifest("default", manifest_url)
    git_server.remove_repo("foo.git")
    git_worktree.sync()
    assert not git_worktree.get_git_project("foo")
