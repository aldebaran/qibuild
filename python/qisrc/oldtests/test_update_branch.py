## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest
from qisrc.test.fake_git import FakeGit

def test_simple():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("status", 0, "")
    git.add_result("rebase", 0, "")
    error = git.update_branch("master", "origin")
    assert not error
    git.check()

def test_wrong_branch_fast_forward():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("symbolic-ref", 0, "refs/heads/next")
    git.add_result("symbolic-ref", 0, "refs/heads/next")
    git.add_result("status", 0, "")
    git.add_result("checkout", 0, "")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("merge-base", 0, "local_sha1")
    git.add_result("merge", 0, "")
    git.add_result("checkout", 0, "")
    error = git.update_branch("master", "origin")
    assert not error
    git.check()

def test_wrong_branch_non_fast_foward():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("symbolic-ref", 0, "refs/heads/next")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("merge-base", 0, "other_sha1")
    error = git.update_branch("master", "origin")
    assert "Merge is not fast-forward" in error
    assert "you are not on master" in error
    git.check()

def test_wrong_branch_not_clean():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("symbolic-ref", 0, "refs/heads/next")
    git.add_result("symbolic-ref", 0, "refs/heads/next")
    git.add_result("status", 0, "Unstaged changes\n M foo.txt\n")
    git.add_result("stash", 0, "")
    git.add_result("checkout", 0, "")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("merge-base", 0, "local_sha1")
    git.add_result("merge", 0, "")
    git.add_result("checkout", 0, "")
    git.add_result("stash", 0, "")
    error = git.update_branch("master", "origin")
    assert not error
    git.check()

def test_first_stash_fails():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    # sometime stash can fails even if git status says the repo is not clean
    git.add_result("status", 1, "Unstaged changes\n submodule bar\n")
    git.add_result("stash", 1, "nothing to stash\n")
    error = git.update_branch("master", "origin")
    assert "Stashing changes failed" in error
    git.check()

def test_stash_pop_fails():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    git.add_result("status", 1, "Unstaged changes\n M foo.txt\n")
    git.add_result("stash", 0, "")
    # Assume foo.txt is created during rebase
    git.add_result("rebase", 0, "")
    git.add_result("stash", 1, "Unstaged changes in foo.txt "
                   "would be overwritten by merge")
    git.add_result("rebase", 0, "")
    error = git.update_branch("master", "origin")
    assert "Stashing back changes failed" in error
    git.check()

def test_rebase_fails():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    git.add_result("status", 0, "")
    git.add_result("rebase", 1, "Conflict in foo.txt")
    git.add_result("rebase", 0, "")
    error = git.update_branch("master", "origin")
    assert "Conflict in foo.txt" in error
    git.check()

# pylint: disable-msg=E1101
@pytest.mark.xfail
def test_stash_then_rebase_fails():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("fetch", 0, "")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    git.add_result("status", 1, "Unstaged changes\n M foo.txt\n")
    git.add_result("stash", 0, "")
    git.add_result("rebase", 1, "Conflict in foo.txt")
    git.add_result("stash", 0, "") # qisrc should stash pop
    error = git.update_branch("master", "origin")
    #assert "Conflict in foo.txt" in error
    git.check()

def test_rebase_abort_fails():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    git.add_result("status", 0, "")
    git.add_result("rebase", 1, "Conflict in foo.txt")
    # Not sure why rebase --abort could fail ...
    git.add_result("rebase", 1, "No space left on device")
    error = git.update_branch("master", "origin")
    assert "Conflict in foo.txt" in error
    assert "rebase --abort failed!" in error
    git.check()

def test_fetch_fails():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    git.add_result("fetch", 2, "could not resolve hostname github.com")
    error = git.update_branch("master", "origin")
    assert "Fetch failed" in error
    assert "github.com" in error
    git.check()

def test_submodules():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "24faae bar (heads/master)\n")
    git.add_result("submodule", 0, "")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    git.add_result("fetch", 0, "")
    git.add_result("show-ref", 0, "local_sha1")
    git.add_result("show-ref", 0, "remote_sha1")
    git.add_result("status", 0, "")
    git.add_result("rebase", 0, "")
    git.update_branch("master", "origin")
    git.check()

def test_broken_submodules():
    git = FakeGit("repo")
    git.add_result("submodule", 1, "no submodule mapping found for path 'bar'\n")
    error = git.update_branch("master", "origin")
    assert "Broken submodules" in error

def test_do_not_rebase_when_already_synced():
    git = FakeGit("repo")
    git.add_result("submodule", 0, "")
    git.add_result("symbolic-ref", 0, "refs/heads/master")
    git.add_result("fetch", 0, "same_sha1")
    git.add_result("show-ref", 0, "same_sha1")
    git.add_result("show-ref", 0, "same_sha1")
    error = git.update_branch("master", "origin")
    assert not error
    git.check()
