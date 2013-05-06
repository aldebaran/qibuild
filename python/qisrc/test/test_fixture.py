import os
import qisrc.git

def test_git_server_creates_valid_urls(tmpdir, git_server):
    origin_url = git_server.manifest.get_remote("origin").url
    assert os.path.exists(origin_url)
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.remote_url
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(foo_url)

def test_pushing_files(tmpdir, git_server):
    origin_url = git_server.manifest.get_remote("origin").url
    assert os.path.exists(origin_url)
    foo_repo = git_server.create_repo("foo.git")
    foo_url = foo_repo.remote_url
    foo_clone = tmpdir.mkdir("foo")
    git = qisrc.git.Git(foo_clone.strpath)
    git.clone(foo_url)

    git_server.push_file("foo.git", "README", "This is foo\n")
    git.pull()

    assert foo_clone.join("README").read() == "This is foo\n"


def test_no_review_by_default(tmpdir, git_server):
    foo_repo = git_server.create_repo("foo.git")
    assert foo_repo.remote == "origin"
    assert foo_repo.review is False
    origin = git_server.manifest.get_remote("origin")
    assert origin.review is False

def test_create_review_repos(tmpdir, git_server):
    foo_repo = git_server.create_repo("foo", review=True)
    assert foo_repo.remote == "gerrit"
    assert foo_repo.review is True
    gerrit = git_server.manifest.get_remote("origin")
    assert gerrit.review is False

def test_new_project_under_review(tmpdir, git_server):
    foo_repo = git_server.create_repo("foo.git", review=False)
    assert foo_repo.review is False
    git_server.use_review("foo.git")
    foo_repo = git_server.get_repo("foo.git")
    assert foo_repo.review is True
    assert foo_repo.remote == "gerrit"
    git = qisrc.git.Git(tmpdir.strpath)
    rc, out = git.call("ls-remote", foo_repo.remote_url, raises=False)
    assert rc == 0
