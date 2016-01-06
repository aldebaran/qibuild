## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import qipy.parsers

def test_simple(qipy_action, args):
    qipy_action.add_test_project("a_lib")
    python_worktree = qipy.parsers.get_python_worktree(args)
    qipy_action("bootstrap")
    venv_path = python_worktree.venv_path
    qipy_action("clean")
    assert os.path.exists(venv_path)
    qipy_action("clean", "--force")
    assert not os.path.exists(venv_path)
