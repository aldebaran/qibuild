import qibuild.build_config

def test_default_is_debug(build_worktree):
    build_config = qibuild.build_config.CMakeBuildConfig()
    assert build_config.cmake_args(build_worktree) == ["-DCMAKE_BUILD_TYPE=Debug"]

def test_read_cmake_generator(build_worktree):
    build_config = qibuild.build_config.CMakeBuildConfig()
    build_config.cmake_generator = "Ninja"
    assert build_config.cmake_args(build_worktree) == \
            ["-GNinja", "-DCMAKE_BUILD_TYPE=Debug"]

def test_read_build_type(build_worktree):
    build_config = qibuild.build_config.CMakeBuildConfig()
    build_config.build_type = "Release"
    assert build_config.cmake_args(build_worktree) == ["-DCMAKE_BUILD_TYPE=Release"]

def test_read_profiles(build_worktree):
    build_worktree.configure_build_profile("foo", [("WITH_FOO", "ON")])
    build_config = qibuild.build_config.CMakeBuildConfig()
    build_config.profiles = ["foo"]
    assert build_config.cmake_args(build_worktree) == \
            ["-DCMAKE_BUILD_TYPE=Debug", "-DWITH_FOO=ON"]

def test_users_flags_taken_last(build_worktree):
    build_worktree.configure_build_profile("foo", [("WITH_FOO", "ON")])
    build_config = qibuild.build_config.CMakeBuildConfig()
    build_config.profiles = ["foo"]
    build_config.user_flags = [("WITH_FOO", "OFF")]
    assert build_config.cmake_args(build_worktree) == \
            ["-DCMAKE_BUILD_TYPE=Debug",
             "-DWITH_FOO=ON",
             "-DWITH_FOO=OFF"]
