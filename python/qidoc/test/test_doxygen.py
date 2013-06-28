import os

import qidoc.doxygen

def test_forced_settings(doc_worktree):
    foo_dox = doc_worktree.create_doxygen_project("foo")
    foo_dox.configure()
    conf = qidoc.doxygen.read_doxyfile(foo_dox.out_doxyfile)
    assert conf["OUTPUT_DIRECTORY"] == foo_dox.build_dir
    assert conf["GENERATE_LATEX"] == "NO"
    assert conf["GENERATE_XML"] == "YES"

def test_rewrite_relative_paths(doc_worktree):
    foo_dox = doc_worktree.create_doxygen_project("foo")
    conf = dict()
    conf["INPUT"] = "src/ include/foo"
    conf["EXAMPLE_PATH"] = "example"
    qidoc.doxygen.write_doxyfile(conf, foo_dox.in_doxyfile)
    foo_dox.configure()
    conf = qidoc.doxygen.read_doxyfile(foo_dox.out_doxyfile)
    assert conf["EXAMPLE_PATH"] == os.path.join(foo_dox.path, "example")
    assert conf["INPUT"] == "%s %s" % (
        os.path.join(foo_dox.path, "src/"),
        os.path.join(foo_dox.path, "include/foo")
    )

def test_with_version(doc_worktree):
    foo_dox = doc_worktree.create_doxygen_project("foo")
    foo_dox.configure(version="1.2.3")
    conf = qidoc.doxygen.read_doxyfile(foo_dox.out_doxyfile)
    assert conf["PROJECT_NUMBER"] == "1.2.3"

def test_build(doc_worktree):
    doc_worktree.add_test_project("libqi")
    qi_dox = doc_worktree.get_doc_project("qi-api", raises=True)

    qi_dox.configure()
    qi_dox.build()

    assert os.path.exists(qi_dox.index_html)
