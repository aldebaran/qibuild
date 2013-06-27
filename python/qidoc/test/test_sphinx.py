import os

import py

def test_no_templates(doc_worktree):
    foo_sphinx = doc_worktree.create_sphinx_project("foo")
    # pylint: disable-msg=E1101
    foo_path = py.path.local(foo_sphinx.path)
    conf_py = foo_path.join("source", "conf.py").ensure(file=True)
    settings = """ \
# My custom settings

project = "foo"
version = "2.3"
"""
    conf_py.write(settings)
    foo_sphinx.configure()
    conf_py = foo_path.join("build-doc", "conf.py")
    assert conf_py.read() == settings

def test_build(doc_worktree):
    doc_worktree.add_test_project("libqi")
    qi_sphinx = doc_worktree.get_doc_project("qi-sphinx", raises=True)

    qi_sphinx.configure()
    qi_sphinx.build()

    assert os.path.exists(qi_sphinx.index_html)
