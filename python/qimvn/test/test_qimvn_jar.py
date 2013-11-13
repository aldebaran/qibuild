import pytest
import os
import qisys
import qibuild.parsers

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qimvn import jar

def get_paths(config=None):
    """ Get project list
    """
    build_worktree = qibuild.parsers.get_build_worktree(None)
    if config:
        build_worktree.set_active_config(config)
    projects = build_worktree.build_projects

    paths = list()
    for proj in projects:
        paths += [proj.sdk_directory]
    return paths

def test_jar_creation(qibuild_action, qimvn_action):
    """ Test if jar can find element in worktree and
        if a jar is created.
    """
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")

    jarname = "test.jar"
    jarpath = jar.jar(jarname, ["hello", "world"], get_paths())
    assert jarpath
    assert os.path.exists(jarpath)
    assert os.path.exists(os.path.join("./", jarname))

def test_package_multiple_target(qibuild_action, qimvn_action):
    """ Test if jar command can package multiple element.
    """
    project = qibuild_action.add_test_project("testjni")
    project.configure()
    project.build()

    jarname = "test.jar"
    jarpath = jar.jar(jarname, ["one", "two", "three", "four"], get_paths())
    assert jarpath
    assert os.path.exists(jarpath)
    assert qimvn_action.is_in_jar(jarpath, "idontexist") == False
    assert qimvn_action.is_in_jar(jarpath, "one")
    assert qimvn_action.is_in_jar(jarpath, "two")
    assert qimvn_action.is_in_jar(jarpath, "three")
    assert qimvn_action.is_in_jar(jarpath, "four")

def test_without_input_files(qibuild_action):
    """ Test that exception is raised if no input file is given.
    """
    with pytest.raises(Exception) as e:
        jar.jar("foo.jar", list(), get_paths())
    assert e.value[0] == "Missing arguments : Files to package"

def test_jar_path(qibuild_action, qimvn_action):
    """ Test if jar command can create jar in a specified directory
    """
    project = qibuild_action.add_test_project("testjni")
    project.configure()
    project.build()

    jar_dirname = os.path.join(os.getcwd(), "./path/to/jar")
    jarname = "test.jar"
    qisys.sh.mkdir(jar_dirname, recursive=True)
    assert os.path.exists(jar_dirname)

    jar_path = os.path.join(jar_dirname, jarname)
    jar_path = jar.jar(jar_path, ["one", "two", "three", "four"], get_paths())
    assert os.path.exists(jar_path)

def test_toolchain(tmpdir, monkeypatch, qimvn_action):
    """ Test packaging using a toolchain
    """
    monkeypatch.chdir(tmpdir)
    qibuild_action = QiBuildAction()
    qitoolchain_action = QiToolchainAction()
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qitoolchain_action("add-package", "-c", "foo", "world", world_package)

    qibuild_action.chdir("hello")
    qibuild_action("configure", "-c", "foo")
    qibuild_action("make", "-c", "foo")

    jarname = "test.jar"
    jarpath = jar.jar(jarname, ["hello", "world"], get_paths(config="foo"))
    assert jarpath
    assert os.path.exists(jarpath)
    assert os.path.exists(os.path.join("./", jarname))
