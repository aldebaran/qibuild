#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest
import six

import qipy.parsers


@pytest.mark.skipif(six.PY3, reason="Only testable with python 2.7")
def test_simple(qipy_action, args):
    """ Test Simple """
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
