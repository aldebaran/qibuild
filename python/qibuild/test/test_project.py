import qisys.worktree
import qibuild.toc

def test_qiproject_but_no_cmake(tmpdir):
    worktree_xml = tmpdir.join(".qi", "worktree.xml").ensure(file=True)
    worktree_xml.write(""" \
<worktree>
  <project src="foo" />
</worktree>
""")
    foo_qiproj = tmpdir.join("foo", "qiproject.xml").ensure(file=True)
    foo_qiproj.write(""" \
<project name="foo">
  <project src="bar" />
</project>
""")
    foo_cmake = tmpdir.join("foo", "CMakeLists.txt").ensure(file=True)
    bar_qiproj = tmpdir.join("foo", "bar", "qiproject.xml").ensure(file=True)
    bar_qiproj.write(""" \
<project />
""")
    tmpdir.join("foo", "bar", "CMakeLists.txt").ensure(file=True)
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    toc = qibuild.toc.Toc(worktree)
