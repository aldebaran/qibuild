import os

import qisys.sh

from qidoc.test.conftest import TestDocWorkTree
import qidoc.convert

def test_convert_handle_src(worktree):
    foo_proj = worktree.create_project("foo")
    bar_proj = worktree.create_project("foo/bar")
    xml = """
<project>
  <doxydoc name="a_doxy" src="bar" />
</project>
"""
    with open(foo_proj.qiproject_xml, "w") as fp:
        fp.write(xml)

    qidoc.convert.convert_project(foo_proj)

    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert len(doc_projects) == 1
    assert doc_projects[0].src == "foo/bar"


def test_convert_add_subprojects(worktree):
    foo_proj = worktree.create_project("foo")
    bar_path = os.path.join(foo_proj.path, "bar")
    qisys.sh.mkdir(bar_path)
    xml = """
<project>
  <doxydoc name="a_doxy" src="bar" />
</project>
"""
    with open(foo_proj.qiproject_xml, "w") as fp:
        fp.write(xml)

    qidoc.convert.convert_project(foo_proj)

    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert len(doc_projects) == 1
    assert doc_projects[0].src == "foo/bar"


