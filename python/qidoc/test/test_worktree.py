from qidoc.test.conftest import TestDocWorkTree

import pytest

def test_qidoc2_happy(qidoc_action):
    qidoc_action.add_test_project("qidoc2/templates")
    qidoc_action.add_test_project("qidoc2/happy")
    import ipdb; ipdb.set_trace()
    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert len(doc_projects) == 3
    assert doc_projects[0].name == "a_doxy"
    assert doc_projects[1].name == "b_doxy"
    assert doc_projects[1].depends == ["a_doxy"]
    assert doc_projects[2].name == "c_sphinx"
    assert doc_projects[2].depends == ["b_doxy"]

    tmpl_proj = doc_worktree.template_project
    assert tmpl_proj.src == "qidoc2/templates"



# pylint: disable-msg=E1101
@pytest.mark.xfail
def test_convert_from_qi2(qidoc_action):
    qidoc_action.add_test_project("qidoc2/with_src")
    qidoc_action("convert-worktree")
    doc_worktree = TestDocWorkTree()
    assert len(doc_worktree.doc_projects) == 3
