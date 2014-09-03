import os
import zipfile

import qibuild.worktree
import qibuild.cmake_builder
import qipy.worktree
import qipy.python_builder
import qilinguist.worktree
import qilinguist.builder
import qipkg.metabuilder

def test_meta_builder(qipkg_action):

    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("d_pkg")
    meta_pkg_proj = qipkg_action.add_test_project("meta_pkg")
    meta_pml = os.path.join(meta_pkg_proj.path, "meta_pkg.mpml")

    worktree = qipkg_action.worktree
    meta_pml_builder = qipkg.metabuilder.MetaPMLBuilder(worktree, meta_pml)

    meta_pml_builder.configure()
    meta_pml_builder.build()
    pkg_path = meta_pml_builder.make_package(with_breakpad=True)
    contents = list()
    archive = zipfile.ZipFile(pkg_path)
    for fileinfo in archive.infolist():
        contents.append(fileinfo.filename)
    assert contents == ['a-0.1.pkg', 'a-0.1-symbols.zip', 'd-0.1.pkg']
