import qibuild.build_config

def test_default_is_debug(build_worktree):
    assert build_worktree.build_config.cmake_args(build_worktree) == \
            ["-DCMAKE_BUILD_TYPE=Debug"]

def test_read_cmake_gerenator(build_worktree):
    build_config = build_worktree.build_config
    build_config.cmake_generator = "Ninja"
    assert build_config.cmake_args(build_worktree) == \
            ["-GNinja", "-DCMAKE_BUILD_TYPE=Debug"]

def test_read_profiles(build_worktree):
    build_worktree.add_profile("foo", (("WITH_FOO", "ON"),))
    build_config = build_worktree.build_config
    build_config.profiles = ["foo"]
    assert build_config.cmake_args(build_worktree) == list()
