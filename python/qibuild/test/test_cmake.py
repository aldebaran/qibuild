import os
import py

import qibuild.cmake

def test_get_cmake_qibuild_dir_no_worktree():
    res = qibuild.cmake.get_cmake_qibuild_dir()
    assert os.path.exists(os.path.join(res, "qibuild/general.cmake"))

def test_get_cmake_qibuild_dir_with_worktree(worktree):
    qibuild_proj = worktree.add_project("tools/qibuild")
    # pylint: disable-msg=E1101
    qibuild_proj_path = py.path.local(qibuild_proj.path)
    qibuild_proj_path.ensure("cmake", "qibuild", "qibuild-config.cmake", file=True)
    res = qibuild.cmake.get_cmake_qibuild_dir(worktree=worktree)
    assert res == qibuild_proj_path.join("cmake").strpath
