import os

import py

def test_no_templates(doc_worktree):
    foo_sphinx = doc_worktree.create_sphinx_project("foo")
    # pylint: disable-msg=E1101
    foo_path = py.path.local(foo_sphinx.path)
    conf_py = foo_path.join("source", "conf.py").ensure(file=True)
    settings = """ \
# My custom settings

project = "myfoo"
version = "2.3"
"""
    conf_py.write(settings)
    foo_sphinx.configure()
    conf_py = foo_path.join("build-doc", "conf.py")
    assert conf_py.read() == settings

def test_sets_project_name_when_not_defined(doc_worktree):
    foo_sphinx = doc_worktree.create_sphinx_project("foo")
    # pylint: disable-msg=E1101
    foo_path = py.path.local(foo_sphinx.path)
    conf_py = foo_path.join("source", "conf.py").ensure(file=True)
    foo_sphinx.configure()
    conf_py = foo_path.join("build-doc", "conf.py")
    assert 'project = "foo"' in conf_py.read()


def test_version(doc_worktree):
    foo_sphinx = doc_worktree.create_sphinx_project("foo")
    # pylint: disable-msg=E1101
    foo_path = py.path.local(foo_sphinx.path)
    conf_py = foo_path.join("source", "conf.py").ensure(file=True)
    conf_py.write('project = "foo"\n')
    foo_sphinx.configure(version="1.2.3")
    conf_py = foo_path.join("build-doc", "conf.py").read()
    assert 'version = "1.2.3"' in conf_py

def test_with_template(doc_worktree):
    foo_sphinx = doc_worktree.create_sphinx_project("foo")
    doc_worktree.add_templates()
    # pylint: disable-msg=E1101
    foo_path = py.path.local(foo_sphinx.path)
    conf_py = foo_path.join("source", "conf.in.py").ensure(file=True)
    settings = """\
# My custom settings

project = "foo"
"""
    conf_py.write(settings)
    foo_sphinx.configure(version="1.2.3")
    conf_py = foo_path.join("build-doc", "conf.py").read()
    conf_dict = dict()
    assert "# My custom settings" in conf_py
    exec(conf_py, conf_dict)
    assert conf_dict["version"] == "1.2.3"
    expected = doc_worktree.template_project.themes_path
    assert conf_dict["html_theme_path"] == [expected]


def test_build(doc_worktree):
    doc_worktree.add_test_project("libqi")
    qi_sphinx = doc_worktree.get_doc_project("qi-sphinx", raises=True)

    qi_sphinx.configure()
    qi_sphinx.build()

    assert os.path.exists(qi_sphinx.index_html)

def test_prebuild(doc_worktree):
    doc_worktree.add_test_project("prebuild")
    qi_sphinx = doc_worktree.get_doc_project("prebuild")
    qi_sphinx.configure()
    qi_sphinx.build(werror=True)


def test_examples(doc_worktree, tmpdir):
    examples_proj = doc_worktree.add_test_project("examples")
    examples_proj.configure()
    examples_proj.build(werror=True)
    dest = tmpdir.mkdir("dest")
    examples_proj.install(dest.strpath)
    assert dest.join("samples", "a", "Makefile").check(file=True)

