import os

def test_dependencies_cmake(build_worktree):
    hello_proj = build_worktree.create_project("hello")
    hello_proj.write_dependencies_cmake(list())
    dep_cmake = os.path.join(hello_proj.build_directory,
                             "dependencies.cmake")
    # only way to check this really works is to build some
    # cmake projects, so no other assertions here
    assert os.path.exists(dep_cmake)
