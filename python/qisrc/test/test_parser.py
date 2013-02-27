import qisys.sh
import qisys.parsers
import qisrc.git
import qisrc.parsers
import qisrc.worktree

def test_guess_git_repo(tmpdir, args):
    worktree = qisys.worktree.create(tmpdir.strpath)
    foo = tmpdir.mkdir("foo")
    bar = foo.mkdir("bar")
    foo.join("qiproject.xml").write("""<project>
  <project src="bar" />
</project>
""")
    worktree.add_project("foo")
    git_worktree = qisrc.worktree.GitWorkTree(worktree)
    git = qisrc.git.Git(foo.strpath)
    git.init()

    with qisys.sh.change_cwd(bar.strpath):
        assert qisys.parsers.get_projects(worktree, args)[0].src == "foo/bar"
        assert qisrc.parsers.get_git_projects(git_worktree, args)[0].src == "foo"

