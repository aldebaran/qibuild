import qisys.sh
import qisys.parsers
import qisrc.git
import qisrc.parsers
import qisrc.worktree

from qibuild.test.conftest import TestBuildWorkTree
from qisrc.test.conftest import TestGitWorkTree
def test_guess_git_repo(tmpdir, args):
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    foo = tmpdir.mkdir("foo")
    bar = foo.mkdir("bar")
    foo.join("qiproject.xml").write("""<project>
  <project src="bar" />
</project>
""")
    worktree.add_project("foo")
    git = qisrc.git.Git(foo.strpath)
    git.init()
    git_worktree = qisrc.worktree.GitWorkTree(worktree)

    with qisys.sh.change_cwd(bar.strpath):
        assert qisys.parsers.get_projects(worktree, args)[0].src == "foo/bar"
        assert qisrc.parsers.get_git_projects(git_worktree, args)[0].src == "foo"

def test_using_build_deps(cd_to_tmpdir, monkeypatch, args):
    build_worktree = TestBuildWorkTree()
    foo = build_worktree.create_project("foo")
    world = build_worktree.create_project("world")
    hello = build_worktree.create_project("hello", depends=["world"])
    git = qisrc.git.Git(foo.path)
    git.init()
    git = qisrc.git.Git(world.path)
    git.init()
    git = qisrc.git.Git(hello.path)
    git.init()
    git_worktree = TestGitWorkTree()
    monkeypatch.chdir("hello")
    projs = qisrc.parsers.get_git_projects(git_worktree, args)
    assert [x.src for x in projs] == ["hello"]
    args.use_deps = True
    projs = qisrc.parsers.get_git_projects(git_worktree, args)
    assert [x.src for x in projs] == ["world", "hello"]
    projs = qisrc.parsers.get_git_projects(git_worktree, args, default_all=True)
    assert [x.src for x in projs] == ["world", "hello"]
