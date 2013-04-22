from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qibuild import find

def test_find_target_in_project_cmake(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    record_messages.reset()
    qibuild_action("find", "--cmake", "hello", "world")
    assert record_messages.find("WORLD_LIBRARIES")

def test_find_target_in_toolchain_package_cmake(tmpdir, monkeypatch,
                                          record_messages):
    monkeypatch.chdir(tmpdir)
    qibuild_action = QiBuildAction(worktree_root=tmpdir.strpath)
    qitoolchain_action = QiToolchainAction(worktree_root=tmpdir.strpath)
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qitoolchain_action("add-package", "-c", "foo", "world", world_package)
    build_worktree.worktree.remove_project("world", from_disk=True)

    record_messages.reset()
    qibuild_action.chdir("hello")
    qibuild_action("configure", "-c", "foo")
    qibuild_action("find", "--cmake", "world", "-c", "foo")

    assert record_messages.find("WORLD_LIBRARIES")

def test_find_target(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")

    record_messages.reset()
    qibuild_action("find", "hello", "world")
    assert record_messages.find(find.library_name("world"))

    record_messages.reset()
    qibuild_action("find", "hello", "libworld")
    assert record_messages.find(find.library_name("world")) is None

def test_find_target_in_toolchain_package(tmpdir, monkeypatch,
                                          record_messages):
    monkeypatch.chdir(tmpdir)
    qibuild_action = QiBuildAction(worktree_root=tmpdir.strpath)
    qitoolchain_action = QiToolchainAction(worktree_root=tmpdir.strpath)
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qitoolchain_action("add-package", "-c", "foo", "world", world_package)

    qibuild_action.chdir("hello")
    qibuild_action("configure", "-c", "foo")
    qibuild_action("make", "-c", "foo")

    record_messages.reset()
    qibuild_action("find", "world", "-c", "foo")
    assert record_messages.find(find.library_name("world"))

    record_messages.reset()
    qibuild_action("find", "hello", "-c", "foo")
    assert record_messages.find(find.binary_name("hello"))

    record_messages.reset()
    qibuild_action("find", "libeggs", "-c", "foo")
    assert record_messages.find("libeggs") is None

def test_library_name_abstraction():
    assert find.library_name("foo", os="Windows") == "foo.dll"
    assert find.library_name("foo", debug=True, os="Windows") == "foo_d.dll"
    assert find.library_name("foo", dynamic=False, os="Windows") == "foo.lib"
    assert find.library_name("foo", dynamic=False, debug=True, os="Windows") == "foo_d.lib"

    assert find.library_name("foo", os="Linux") == "libfoo.so"
    assert find.library_name("foo", debug=True, os="Linux") == "libfoo.so"
    assert find.library_name("foo", dynamic=False, os="Linux") == "libfoo.a"
    assert find.library_name("foo", dynamic=False, debug=True, os="Linux") == "libfoo.a"

    assert find.library_name("foo", os="Mac") == "libfoo.dylib"
    assert find.library_name("foo", debug=True, os="Mac") == "libfoo.dylib"
    assert find.library_name("foo", dynamic=False, os="Mac") == "libfoo.dylib"
    assert find.library_name("foo", dynamic=False, debug=True, os="Mac") == "libfoo.dylib"

    assert find.library_name("foo", os="Bar") == "libfoo"

def test_binary_name_abstraction():
    assert find.binary_name("foo", os="Windows") == "foo.exe"
    assert find.binary_name("foo", os="Windows", debug=True) == "foo_d.exe"

    assert find.binary_name("foo", os="Mac") == "foo"
    assert find.binary_name("foo", os="Mac", debug=True) == "foo"

    assert find.binary_name("foo", os="Linux") == "foo"
    assert find.binary_name("foo", os="Linux", debug=True) == "foo"
