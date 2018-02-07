# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import os
import pytest

import qipy.parsers


def test_simple(qipy_action, args):
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "--no-site-packages", "pip", "virtualenv", "ipython<=5")
    python_worktree = qipy.parsers.get_python_worktree(args)
    venv_path = python_worktree.venv_path
    jinja_path = os.path.join(venv_path, "lib", "python2.7", "site-packages", "jinja")
    if os.path.exists(jinja_path):
        pytest.fail("Jinja already installed in virtualenv")
    qipy_action("pip", "install", "jinja")
    if not os.path.exists(jinja_path):
        pytest.fail("Jinja not installed in virtualenv")
