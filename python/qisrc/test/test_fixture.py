import os
import qisrc.git

from qibuild.test.conftest import TestBuildWorkTree

def test_git_server_creates_valid_urls(tmpdir, git_server):
    origin_url = git_server.manifest.get_remote("origin").url
    assert os.path.exists(origin_url)
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.clone_url
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(foo_url)

def test_pushing_files(tmpdir, git_server):
    origin_url = git_server.manifest.get_remote("origin").url
    assert os.path.exists(origin_url)
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.clone_url
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(foo_url)

    git_server.push_file("foo.git", "README", "This is foo\n")
    git.pull()

    assert foo_clone.join("README").read() == "This is foo\n"

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
    qisrc_action("manifest", "--add", "default", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    assert build_worktree.get_build_project("world")

def test_change_branch(git_server):
    foo_repo = git_server.create_repo("foo.git")
    assert foo_repo.default_branch == "master"
    git_server.change_branch(foo_repo, "devel")
    assert foo_repo.default_branch == "devel"
