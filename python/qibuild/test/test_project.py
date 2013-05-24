import os

import pytest

def test_dependencies_cmake(build_worktree):
    hello_proj = build_worktree.create_project("hello")
    hello_proj.write_dependencies_cmake(list())
    dep_cmake = os.path.join(hello_proj.build_directory,
                             "dependencies.cmake")
    # only way to check this really works is to build some
    # cmake projects, so no other assertions here
    assert os.path.exists(dep_cmake)

def test_parse_num_jobs_happy_path(build_worktree):
    hello = build_worktree.create_project("hello")
    assert hello.parse_num_jobs(3, cmake_generator="Unix Makefiles") ==  ["-j", "3"]
    assert hello.parse_num_jobs(2, cmake_generator="Ninja") ==  ["-j", "2"]
    # 1 is the default value, but don't force -j1 when using Ninja
    assert hello.parse_num_jobs(1, cmake_generator="Ninja") ==  list()

def test_parse_num_jobs_unsupported_generator(build_worktree):
    hello = build_worktree.create_project("hello")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        hello.parse_num_jobs(3, cmake_generator="NMake Makefiles") ==  list()
    assert "-j is not supported for NMake Makefiles" in str(e.value)

def test_parse_num_jobs_no_dash_j(build_worktree, record_messages):
    hello = build_worktree.create_project("hello")
    assert hello.parse_num_jobs(3, cmake_generator="Visual Studio 10") ==  list()
    assert record_messages.find("-j is ignored when used with Visual Studio 10")

def test_parse_num_jobs_unknown_generator(build_worktree, record_messages):
    hello = build_worktree.create_project("hello")
    assert hello.parse_num_jobs(3, cmake_generator="KDevelop3") ==  list()
    assert record_messages.find("Unknown generator: KDevelop3")
