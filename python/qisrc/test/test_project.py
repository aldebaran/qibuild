import qisrc.git
from qisrc.git_config import Remote


def test_appy_git_config(git_worktree):
    foo = git_worktree.create_git_project("foo")
    upstream = Remote()
    upstream.name = "upstream"
    upstream.url = "git@srv:bar.git"
    foo.configure_remote(upstream)
    foo.apply_config()

    git = qisrc.git.Git(foo.path)
    assert git.get_config("remote.upstream.url") == "git@srv:bar.git"

    foo.configure_branch("master", tracks="upstream")
    foo.apply_config()
    assert git.get_tracking_branch("master") == "upstream/master"

    foo.configure_branch("feature", tracks="upstream",
                         remote_branch="remote_branch")
    foo.apply_config()
    assert git.get_tracking_branch("feature") == "upstream/remote_branch"

def test_warn_on_change(git_worktree, record_messages):
    foo = git_worktree.create_git_project("foo")
    origin = Remote()
    origin.name = "origin"
    origin.url =  "git@srv:foo.git"
    foo.configure_remote(origin)
    foo.configure_branch("master", tracks="origin", default=True)
    origin2 = Remote()
    origin2.name = "origin"
    origin2.url =  "git@srv:libfoo.git"
    foo.configure_remote(origin2)
    assert record_messages.find("remote url changed")
    foo.configure_branch("next", default=True)
    assert record_messages.find("default branch changed")
    gerrit = Remote()
    gerrit.name = "gerrit"
    gerrit.url =  "http://gerrit/libfoo.git"
    foo.configure_remote(gerrit)
    foo.configure_branch("next", tracks="gerrit")
    assert record_messages.find("now tracks gerrit instead")

def test_setting_default_branch(git_worktree):
    foo = git_worktree.create_git_project("foo")
    foo.configure_branch("master", default=False)
    assert foo.default_branch is None
    foo.configure_branch("master", default=True)
    assert foo.default_branch.name == "master"

def test_change_default_branch(git_worktree):
    foo_proj = git_worktree.create_git_project("foo")
    foo_proj.configure_branch("master", default=True)
    foo_proj.configure_branch("devel", default=True)
    assert foo_proj.default_branch.name == "devel"
