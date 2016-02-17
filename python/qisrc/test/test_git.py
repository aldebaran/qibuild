## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import qisys.sh
import qisrc.git
from qisrc.test.conftest import TestGit

def test_name_from_url_common():
    examples = [
        ("git@git:foo/bar.git", "foo/bar.git"),
        ("/srv/git/foo/bar.git", "bar.git"),
        ("file:///srv/git/foo/bar.git", "bar.git"),
        ("ssh://git@review:29418/foo/bar.git", "foo/bar.git"),
        ("ssh://git@example.com/spam/eggs.git", "spam/eggs.git"),
        ("ssh://git@example.com/eggs.git", "eggs.git"),
        ("http://github.com/john/bar.git", "john/bar.git")

    ]
    for (url, expected) in  examples:
        actual = qisrc.git.name_from_url(url)
        assert actual == expected


def test_name_from_url_win():
    if not os.name == 'nt':
        return
    url = r"file:///c:/path/to/bar.git"
    assert qisrc.git.name_from_url(url) == "bar.git"

def test_set_tracking_branch_on_empty_repo(tmpdir):
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    ret = git.set_tracking_branch("master", "master", "origin")
    assert ret is False

def test_set_tracking_branch_existing_branch_tracking_none(tmpdir):
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    git.commit("-m", "empty", "--allow-empty")
    ret = git.set_tracking_branch("master", "master", "origin")
    assert ret is True

def test_set_tracking_branch_existing_branch_tracking_ok(tmpdir):
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    git.commit("-m", "empty", "--allow-empty")
    git.set_tracking_branch("master", "origin")
    ret = git.set_tracking_branch("master", "origin")
    assert ret is True

def test_set_tracking_branch_existing_branch_tracking_other(tmpdir):
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    git.commit("-m", "empty", "--allow-empty")
    git.set_tracking_branch("master", "origin")
    ret = git.set_tracking_branch("master", "other")
    assert ret is True

def test_changelog(cd_to_tmpdir):
    git = TestGit()
    git.initialize()
    message_1 = "mess1"
    git.commit_file("foo.txt", "foo\n", message=message_1)
    message_2 = "mess2"
    git.commit_file("foo.txt", "bar\n", message=message_2)
    commits = git.get_log("HEAD~2", "HEAD")
    assert len(commits) == 2
    assert commits[0]["message"] == message_1
    assert commits[1]["message"] == message_2

def test_get_repo_root(tmpdir):
    root = tmpdir.ensure("CrazyCase", dir=True)
    git = TestGit(root.strpath)
    git.initialize()
    subdir = root.ensure("some" , "subdir", dir=True)
    actual = qisrc.git.get_repo_root(subdir.strpath)
    expected = qisys.sh.to_native_path(root.strpath)
    assert actual == expected

def test_safe_checkout(cd_to_tmpdir, git_server):
    git_server.create_repo("foo.git")
    git = TestGit()
    git.clone(git_server.srv.join("foo.git").strpath)
    ok, mess = git.safe_checkout("devel", "origin")
    assert git.get_current_branch() == "devel"
    assert ok

def test_ignores_env(tmpdir, monkeypatch):
    repo1 = tmpdir.mkdir("repo1")
    repo2 = tmpdir.mkdir("repo2")
    git1 = TestGit(repo1.strpath)
    git2 = TestGit(repo2.strpath)
    git1.initialize()
    git2.initialize()
    untracked = repo1.join("untracked")
    untracked.ensure(file=True)
    monkeypatch.setenv("GIT_DIR", repo1.join(".git").strpath)
    monkeypatch.setenv("GIT_WORK_TREE", repo1.strpath)
    git2.call("clean", "--force")
    assert untracked.check(file=1)
