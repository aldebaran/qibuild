#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import qipy.parsers


def test_simple(qipy_action, args):
    """ Test Simple """
    qipy_action.add_test_project("a_lib")
    python_worktree = qipy.parsers.get_python_worktree(args)
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    venv_path = python_worktree.venv_path
    qipy_action("clean")
    assert os.path.exists(venv_path)
    qipy_action("clean", "--force")
    assert not os.path.exists(venv_path)
