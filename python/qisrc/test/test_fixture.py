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
