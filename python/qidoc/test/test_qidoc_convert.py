from qidoc.test.conftest import TestDocWorkTree

def test_convert_from_qi2(qidoc_action):
    qidoc_action.add_test_project("qidoc2/with_src")
    qidoc_action("convert-worktree")
    doc_worktree = TestDocWorkTree()
    assert len(doc_worktree.doc_projects) == 3
