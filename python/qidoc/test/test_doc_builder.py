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
    world_proj = doc_worktree.add_test_project("world")
    hello_proj = doc_worktree.add_test_project("hello")
    doc_builder = DocBuilder(doc_worktree)
    hello_inst = tmpdir.join("inst", "hello")
    doc_builder.base_project = hello_proj
    doc_builder.configure()
    doc_builder.build()
    doc_builder.install(hello_inst.strpath)
    hello_index = hello_inst.join("index.html")
    assert "hello" in hello_index.read()
    world_index = hello_inst.join("ref/world/index.html")
    assert "world" in world_index.read()


def test_install_doxy(doc_worktree, tmpdir):
    qi_api_proj = doc_worktree.add_test_project("libqi/doc/doxygen")
    assert qi_api_proj
    inst_dir = tmpdir.join("inst")
    doc_builder = DocBuilder(doc_worktree)
    doc_builder.base_project = qi_api_proj
    doc_builder.configure()
    doc_builder.build()
    doc_builder.install(inst_dir.strpath)
    assert "qi" in inst_dir.join("index.html").read()

