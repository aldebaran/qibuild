## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import zipfile

import qisys.command
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
    meta_pml_builder = qipkg.metabuilder.MetaPMLBuilder(meta_pml, worktree=worktree)

    meta_pml_builder.configure()
    meta_pml_builder.build()
    dump_syms = qisys.command.find_program("dump_syms")
    if dump_syms:
        with_breakpad = True
    else:
        with_breakpad = False
    packages = meta_pml_builder.package(with_breakpad=with_breakpad)
    contents = [os.path.basename(x) for x in packages]
    if with_breakpad:
        assert contents == ['a-0.1.pkg', 'a-0.1-symbols.zip', 'd-0.1.pkg']
    else:
        assert contents == ['a-0.1.pkg', 'd-0.1.pkg']
