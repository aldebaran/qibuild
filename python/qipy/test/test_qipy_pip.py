# coding: utf-8
## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import pytest

import qipy.parsers


def test_simple(qipy_action, args):
    qipy_action("bootstrap")
    python_worktree = qipy.parsers.get_python_worktree(args)
    venv_path = python_worktree.venv_path
    jinja_path = os.path.join(venv_path, "lib", "python2.7", "site-packages", "jinja")
    if os.path.exists(jinja_path):
        pytest.fail("Jinja already installed in virtualenv")
    qipy_action("pip", "install", "jinja")
    if not os.path.exists(jinja_path):
        pytest.fail("Jinja not installed in virtualenv")
