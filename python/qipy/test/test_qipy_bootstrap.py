import os

import qisys.sh

from qibuild.test.conftest import qibuild_action  # pylint: disable=unused-import

# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable


def test_simple(qipy_action):
    a_project = qipy_action.add_test_project("a_lib")
    big_project = qipy_action.add_test_project("big_project")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("run", "--no-exec", "--", "python", "-m", "a")
    qipy_action("run", "--no-exec", "--", "python", "-m", "foo.bar.baz")


def test_cpp(qipy_action, qibuild_action):
    qipy_action.add_test_project("c_swig")
    qibuild_action("configure", "swig_eggs")
    qibuild_action("make", "swig_eggs")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("run", "--no-exec", "--", "python", "-c", "import eggs")


def test_with_deps(qipy_action):
    qipy_action.add_test_project("with_deps")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("run", "--no-exec", "--", "python", "-c", "import markdown")


def test_with_distutils(qipy_action):
    qipy_action.add_test_project("with_distutils")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("run", "--no-exec", "foo")


def test_qimodule(qipy_action):
    qipy_action.add_test_project("foomodules")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    sourceme = qipy_action("sourceme")
    bin_path = os.path.dirname(sourceme)
    venv_path = os.path.join(bin_path, "..")
    venv_path = qisys.sh.to_native_path(venv_path)
    for name in ["foo", "bar"]:
        mod_path = os.path.join(venv_path, "share", "qi", "module", "%s.mod" % name)
        with open(mod_path, "r") as fp:
            contents = fp.read()
        assert contents == "python\n"


def test_fails_on_bad_requirements_txt(qipy_action):
    a_project = qipy_action.add_test_project("a_lib")
    requirements_txt = os.path.join(a_project.path, "requirements.txt")
    with open(requirements_txt, "w") as fp:
        fp.write("no such package\n")
    rc = qipy_action("bootstrap", retcode=True)
    assert rc != 0
