import qisys.qixml
import qisys.worktree
import qisrc.worktree

def test_git_worktree(tmpdir):
    tmpdir.mkdir("foo")
    tmpdir.mkdir("bar")
    wt = qisys.worktree.create(tmpdir.strpath)
    wt.add_project("foo")
    wt.add_project("bar")

    tmpdir.join(".qi").join("git.xml").write(""" \
<qigit>
 <project src="bar" branch="next">
    <remote name="origin" url="git@srv:bar.git" />
    <review url="http://gerrit.example.com" />
 </project>
 <project src="baz" branch="master" />
</qigit>
""")


    git_wt = qisrc.worktree.GitWorkTree(wt)
    print git_wt.git_projects
