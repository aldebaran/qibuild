import qisys.sh
import qibuild.build_config
import qitoolchain.toolchain

def test_read_profiles(build_worktree):
    build_worktree.configure_build_profile("foo", [("WITH_FOO", "ON")])
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    build_config.profiles = ["foo"]
    assert build_config.cmake_args == \
            ["-DCMAKE_BUILD_TYPE=Debug", "-DWITH_FOO=ON"]

def test_users_flags_taken_last(build_worktree):
    build_worktree.configure_build_profile("foo", [("WITH_FOO", "ON")])
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    build_config.profiles = ["foo"]
    build_config.user_flags = [("WITH_FOO", "OFF")]
    assert build_config.cmake_args == \
            ["-DCMAKE_BUILD_TYPE=Debug",
             "-DWITH_FOO=ON",
             "-DWITH_FOO=OFF"]


def test_sane_defaults(build_worktree):
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.cmake_generator is None
    assert build_config.build_type == "Debug"
    assert build_config.cmake_args == ["-DCMAKE_BUILD_TYPE=Debug"]

def test_read_qibuild_conf(build_worktree):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    with open(qibuild_xml, "w") as fp:
        fp.write("""
<qibuild>
  <defaults>
    <cmake generator="Ninja" />
  </defaults>
</qibuild>
""")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.cmake_generator == "Ninja"
    assert build_config.cmake_args == \
            ["-GNinja", "-DCMAKE_BUILD_TYPE=Debug"]

def test_read_default_config(build_worktree):
    qitoolchain.toolchain.Toolchain("foo")
    build_worktree.set_default_config("foo")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.toolchain.name == "foo"

def test_use_specific_generator_from_default_config(build_worktree):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    with open(qibuild_xml, "w") as fp:
        fp.write("""
<qibuild>
  <defaults>
    <cmake generator="Ninja" />
  </defaults>
  <config name="vs2010">
    <cmake generator="Visual Studio 2010" />
  </config>
</qibuild>
""")
    qitoolchain.toolchain.Toolchain("vs2010")
    build_worktree.set_default_config("vs2010")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.cmake_generator == "Visual Studio 2010"

def test_set_config_name(build_worktree):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    with open(qibuild_xml, "w") as fp:
        fp.write("""
<qibuild>
  <defaults>
    <cmake generator="Ninja" />
  </defaults>
  <config name="vs2010">
    <cmake generator="Visual Studio 2010" />
  </config>
</qibuild>
""")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.cmake_generator == "Ninja"
    build_config.set_active_config("vs2010")
    assert build_config.cmake_generator == "Visual Studio 2010"

def test_build_env(build_worktree):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    with open(qibuild_xml, "w") as fp:
        fp.write(r"""
<qibuild>
  <defaults>
    <env path="c:\swig" />
  </defaults>
  <config name="mingw">
    <env path="c:\mingw\bin" />
  </config>
</qibuild>
""")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    build_config.set_active_config("mingw")
    path = build_config.build_env["PATH"]
    assert r"c:\swig" in path
    assert r"c:\mingw\bin" in path
