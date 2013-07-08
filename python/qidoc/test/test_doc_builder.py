import mock

from qidoc.test.conftest import TestDocWorkTree
from qidoc.builder import DocBuilder

def test_doc_builder_solve_deps_by_default(doc_worktree):
    qibuild_doc = doc_worktree.create_sphinx_project("qibuild")
    general_doc = doc_worktree.create_sphinx_project("general", depends=["qibuild"])
    doc_builder = DocBuilder(doc_worktree)
    doc_builder.base_project = general_doc
    assert doc_builder.get_dep_projects() == [qibuild_doc, general_doc]

def test_using_dash_s(doc_worktree):
    qibuild_doc = doc_worktree.create_sphinx_project("qibuild")
    general_doc = doc_worktree.create_sphinx_project("general", depends=["qibuild"])
    doc_builder = DocBuilder(doc_worktree)
    doc_builder.base_project = general_doc
    doc_builder.single = True
    assert doc_builder.get_dep_projects() == [general_doc]


def test_base_project_install(doc_worktree, tmpdir):
    qibuild_doc = doc_worktree.create_sphinx_project("qibuild", dest="ref/qibuild")
    general_doc = doc_worktree.create_sphinx_project("general", depends=["qibuild"])
    doc_builder = DocBuilder(doc_worktree)
    doc_builder.base_project = general_doc
    general_inst = tmpdir.join("inst", "general")
    doc_builder.configure()
    doc_builder.build()
    doc_builder.install(general_inst.strpath)
    assert
