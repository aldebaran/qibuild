import qisys.command

def test_running_from_install_dir(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "--runtime", "hello", tmpdir.strpath)

    hello = tmpdir.join("bin").join("hello")
    qisys.command.call([hello.strpath])

    assert not tmpdir.join("include").check()

def test_devel_components_installed_by_default(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "hello", tmpdir.strpath)
    assert tmpdir.join("include").join("world").join("world.h").check()

def test_setting_prefix(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "--prefix=/usr", "--runtime",
                   "hello", tmpdir.strpath)
    hello = tmpdir.join("usr").join("bin").join("hello")
    assert hello.check(file=True)

def test_using_compiled_tool_for_install(qibuild_action, tmpdir):
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("bar")
    qibuild_action("configure", "bar")
    qibuild_action("make", "bar")
    qibuild_action("install", "bar", tmpdir.strpath)

    foo_out = tmpdir.join("share", "foo", "foo.out")
    assert foo_out.check(file=True)

def test_qi_install_cmake(qibuild_action, tmpdir):
    qibuild_action.add_test_project("installme")
    qibuild_action("configure", "installme")
    qibuild_action("make", "installme")
    qibuild_action("install", "installme", tmpdir.strpath)
    assert tmpdir.join("share", "data_star", "foo.dat").check(file=True)
    assert tmpdir.join("share", "data_star", "bar.dat").check(file=True)
    assert tmpdir.join("share", "recurse", "a_dir/a_file").check(file=True)
    assert tmpdir.join("share", "recurse", "a_dir/b_dir/c_dir/d_file").check(file=True)

def test_fails_early(qibuild_action, tmpdir):
    qibuild_action.add_test_project("installme")
    qibuild_action("configure", "installme", "-DFAIL_EMPTY_GLOB=TRUE", raises=True)
    qibuild_action("configure", "installme", "-DFAIL_NON_EXISTING=TRUE", raises=True)
