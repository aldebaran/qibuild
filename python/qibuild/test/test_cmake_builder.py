import qibuild.cmake_builder

import mock
import pytest

def test_calls_configure():
    build_worktree = mock.Mock()
    hello_proj = mock.Mock()
    world_proj = mock.Mock()
    deps_solver = mock.Mock()
    deps_solver.get_dep_projects.return_value = [world_proj, hello_proj]

    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree,
                                                       [hello_proj])
    cmake_builder.deps_solver = deps_solver

    cmake_builder.configure()
    assert world_proj.configure.called
    assert hello_proj.configure.called

def test_forward_args_to_configure():
    build_worktree = mock.Mock()
    deps_solver = mock.Mock()
    hello_proj = mock.Mock()
    deps_solver.get_dep_projects.return_value = [hello_proj]
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree,
                                                       [hello_proj])
    cmake_builder.deps_solver = deps_solver

    cmake_builder.configure(trace_cmake=True)
    hello_proj.configure.assert_called_with(trace_cmake=True)

def test_write_dependencies_cmake_first():
    build_worktree = mock.Mock()
    deps_solver = mock.Mock()
    hello_proj = mock.Mock()
    sdk_dirs = [
        "/path/to/hello/build/sdk",
        "/path/to/world/build/sdk"
    ]
    deps_solver.get_dep_projects.return_value = [hello_proj]
    deps_solver.get_sdk_dirs.return_value = sdk_dirs
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree,
                                                       [hello_proj])
    cmake_builder.deps_solver = deps_solver
    cmake_builder.configure()
    hello_proj.write_dependencies_cmake.assert_called_with(sdk_dirs)

def test_check_configure_has_been_called_before_building(build_worktree):
    hello_proj = build_worktree.create_project("hello")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [hello_proj])

    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.cmake_builder.NotConfigured):
        cmake_builder.build()

def test_default_install(build_worktree, toolchains, tmpdir):
    hello_proj = build_worktree.create_project("hello", rdepends="bar")
    toolchains.create("foo")
    build_worktree.set_active_config("foo")
    toolchains.add_package("foo", "bar")
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, [hello_proj])
    cmake_builder.configure()
    cmake_builder.build()
    cmake_builder.install(tmpdir.strpath)
