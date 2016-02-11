## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import qisrc.git

import pytest

from qibuild.test.conftest import TestBuildWorkTree
from qisrc.test.conftest import TestGit
from qisrc.test.conftest import FakeGit

def test_git_server_creates_valid_urls(tmpdir, git_server):
    origin_url = git_server.manifest.get_remote("origin").url
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.clone_url
    assert foo_url.startswith("file://")
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(foo_url)

def test_switch_manifest_branch(tmpdir, git_server):
    git_server.switch_manifest_branch("devel")
    assert git_server.manifest_branch == "devel"
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(git_server.manifest_url, "--branch",
              git_server.manifest_branch)
    assert git.get_current_branch() == "devel"


def test_pushing_files(tmpdir, git_server):
    origin_url = git_server.manifest.get_remote("origin").url
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.clone_url
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(foo_url)

    git_server.push_file("foo.git", "README", "This is foo\n")
    git.pull()

    assert foo_clone.join("README").read() == "This is foo\n"

def test_create_several_commits(git_server):
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "foo.txt", "change 1")
    git_server.push_file("foo.git", "foo.txt", "change 2")

def test_no_review_by_default(tmpdir, git_server):
    foo_repo = git_server.create_repo("foo.git")
    assert foo_repo.review is False
    origin = git_server.manifest.get_remote("origin")
    assert origin.review is False

def test_create_review_repos(tmpdir, git_server):
    foo_repo = git_server.create_repo("foo", review=True)
    assert foo_repo.review_remote.name == "gerrit"
    assert foo_repo.default_remote.name == "origin"
    git = qisrc.git.Git(tmpdir.strpath)
    rc, out = git.call("ls-remote", foo_repo.clone_url, raises=False)
    assert rc == 0

def test_create_empty_repo(tmpdir, git_server):
    foo_repo = git_server.create_repo("foo", empty=True)
    git = qisrc.git.Git(tmpdir.strpath)
    rc, out = git.call("ls-remote", foo_repo.clone_url, raises=False)
    assert rc == 0
    assert not out

def test_new_project_under_review(tmpdir, git_server):
    foo_repo = git_server.create_repo("foo.git", review=False)
    assert foo_repo.review is False
    git_server.use_review("foo.git")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.review is True
    assert foo_repo.review_remote.name == "gerrit"
    git = qisrc.git.Git(tmpdir.strpath)
    rc, out = git.call("ls-remote", foo_repo.clone_url, raises=False)
    assert rc == 0
    git = qisrc.git.Git(tmpdir.strpath)
    rc, out = git.call("ls-remote", foo_repo.review_remote.url, raises=False)
    assert rc == 0

def test_add_build_project(git_server, qisrc_action):
    git_server.add_qibuild_test_project("world")
    qisrc_action("init", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    assert build_worktree.get_build_project("world")

def test_change_branch(git_server):
    git_server.create_repo("foo.git")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.default_branch == "master"
    git_server.change_branch("foo.git", "devel")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.default_branch == "devel"

def test_push_tags(git_server, tmpdir):
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.clone_url
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    foo = tmpdir.mkdir("foo")
    foo_git = TestGit(foo.strpath)
    foo_git.clone(foo_url)
    assert foo_git.read_file("b.txt") == "b"
    foo_git.reset("--hard", "v0.1")
    #pylint:disable-msg=E1101
    with pytest.raises(Exception):
        foo_git.read_file("b.txt")
    assert foo_git.read_file("a.txt") == "a"

def test_fixed_ref(git_server, tmpdir):
    git_server.create_repo("foo.git")
    git_server.set_fixed_ref("foo.git", "v0.1")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.default_branch is None
    assert foo_repo.fixed_ref == "v0.1"

def test_create_svn_repo(svn_server, tmpdir):
    foo_url = svn_server.create_repo("foo")
    work = tmpdir.mkdir("work")
    svn = qisrc.svn.Svn(work.strpath)
    svn.call("checkout", foo_url)
    foo = work.join("foo")
    foo.check(dir=True)

def test_svn_commit(svn_server, tmpdir):
    foo_url = svn_server.create_repo("foo")
    svn_server.commit_file("foo", "README.txt", "this is a readme\n")
    work = tmpdir.mkdir("work")
    svn = qisrc.svn.Svn(work.strpath)
    svn.call("checkout", foo_url)
    foo = work.join("foo")
    readme = foo.join("README.txt")
    assert readme.read() == "this is a readme\n"

def test_fake_git_persistent_config():
    git1 = FakeGit("repo")
    git1.set_config("foo.bar", 42)
    git2 = FakeGit("repo")
    assert git2.get_config("foo.bar") == 42
    assert git2.get_config("notset") is None

def test_fake_git_fake_call():
    git = FakeGit("repo")
    git.add_result("fetch", 0, "")
    (retcode, _) = git.fetch(raises=False)
    assert retcode == 0
    git2 = FakeGit("repo2")
    git2.add_result("fetch", 2, "Remote end hung up unexpectedly")
    (retcode, out) = git2.fetch(raises=False)
    assert retcode == 2
    assert "Remote end hung up" in out

def test_fake_git_wrong_setup():
    git = FakeGit("repo")
    git.add_result("checkout", 0, "")
    git.checkout("-f", "master")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        git.fetch()
    assert "Unexpected call to fetch" in e.value.args[0]

def test_fake_git_configured_but_not_called_enough():
    git = FakeGit("repo")
    git.add_result("checkout", 0, "")
    git.add_result("checkout", 1, "Unstaged changes")
    git.checkout("next")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        git.check()
    assert "checkout was configured to be called 2 times" in e.value.args[0]
    assert "was only called 1 times" in e.value.args[0]

def test_fake_git_configured_but_not_called():
    git = FakeGit("repo")
    git.add_result("checkout", 1, "")
    git.add_result("reset", 0, "")
    # pylint: disable-msg=E1101
    git.checkout(raises=False)
    with pytest.raises(Exception) as e:
        git.check()
    assert "reset was added as result but never called" in e.value.args[0]

def test_fake_git_commands_are_logged():
    git = FakeGit("repo")
    git.add_result("fetch", 0, "")
    git.add_result("reset", 0, "")
    git.fetch()
    git.reset("--hard", quiet=True)
    calls = git.calls
    assert len(calls) == 2
    assert calls[0][0] == ("fetch",)
    assert calls[1][0] == ("reset", "--hard")
    assert calls[1][1] == {"quiet" : True}
