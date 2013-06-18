import qisys.sh
import qisrc.snapshot
from qisrc.test.conftest import TestGitWorkTree

import pytest

def test_dump_load(tmpdir):
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.sha1s["foo"] = "a42fb"
    snapshot.sha1s["bar"] = "bccad"
    snapshot_txt = tmpdir.join("snapshot.txt").strpath
    snapshot.dump(snapshot_txt)
    snapshot2 = qisrc.snapshot.Snapshot()
    snapshot2.load(snapshot_txt)
    assert snapshot2 == snapshot


def test_generate_load(git_worktree, tmpdir):
    foo_proj = git_worktree.create_git_project("foo")
    foo_git = qisrc.git.Git(foo_proj.path)
    _, foo_ref_expected = foo_git.call("rev-parse", "HEAD", raises=False)
    snapshot_txt = tmpdir.join("snapshot.txt").strpath
    qisrc.snapshot.generate_snapshot(git_worktree, snapshot_txt)
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.load(snapshot_txt)
    foo_ref = snapshot.sha1s["foo"]

    # Make a commit and an other diff
    foo_git.commit("--message", "empty", "--allow-empty")

    qisrc.snapshot.load_snapshot(git_worktree, snapshot_txt)
    _, foo_ref_actual = foo_git.call("rev-parse", "HEAD", raises=False)

    assert foo_ref_actual == foo_ref_expected


def test_incorrect_snapshot(git_worktree, tmpdir):
    foo_proj = git_worktree.create_git_project("foo")
    snapshot_txt = tmpdir.join("snapshot.txt").strpath
    qisrc.snapshot.generate_snapshot(git_worktree, snapshot_txt)
    qisys.sh.rm(foo_proj.path)
    git_worktree2 = TestGitWorkTree()
    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.worktree.NoSuchGitProject) as e:
        qisrc.snapshot.load_snapshot(git_worktree2, snapshot_txt)
    assert e.value.args == ("foo",)


def test_always_fetch(git_worktree, git_server, tmpdir):
    foo_repo = git_server.create_repo("foo.git")
    git_worktree.clone_missing(foo_repo)
    foo_proj = git_worktree.get_git_project("foo")
    git_server.push_file("foo.git", "other.txt", "other change\n")
    foo_git = qisrc.git.Git(foo_proj.path)
    rc, remote_sha1 = foo_git.call("ls-remote", "origin", "refs/heads/master",
                                   raises=False)
    assert rc == 0
    remote_sha1 = remote_sha1.split()[0]

    snapshot = qisrc.snapshot.Snapshot()
    snapshot.sha1s["foo"] = remote_sha1
    snapshot_txt = tmpdir.join("snapshot.txt").strpath
    snapshot.dump(snapshot_txt)

    qisrc.snapshot.load_snapshot(git_worktree, snapshot_txt)
    _, local_sha1 = foo_git.call("rev-parse", "HEAD", raises=False)
    assert local_sha1 == remote_sha1




