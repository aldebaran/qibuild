import os
from qibuild.test.conftest import qibuild_action

def test_simple(qipy_action):
    a_project = qipy_action.add_test_project("a_lib")
    big_project = qipy_action.add_test_project("big_project")
    qipy_action("bootstrap")
    qipy_action("run", "--no-exec", "--", "python", "-m", "a")
    qipy_action("run", "--no-exec", "--", "python", "-m", "foo.bar.baz")

def test_cpp(qipy_action, qibuild_action):
    qipy_action.add_test_project("c_swig")
    qibuild_action("configure", "swig_eggs")
    qibuild_action("make", "swig_eggs")
    qipy_action("bootstrap")
    qipy_action("run", "--no-exec", "--", "python", "-c", "import eggs")

def test_with_deps(qipy_action):
    qipy_action.add_test_project("with_deps")
    qipy_action("bootstrap")
    qipy_action("run", "--no-exec", "--", "python", "-c", "import markdown")

def test_with_distutils(qipy_action):
    qipy_action.add_test_project("with_distutils")
    qipy_action("bootstrap")
    qipy_action("run", "--no-exec", "foo")
