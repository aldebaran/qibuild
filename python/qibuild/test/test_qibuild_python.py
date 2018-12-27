#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Test QiBuild Python
Finding a Python qimodule from C++.
This is higly libqi specific.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.sh
from qipy.test.conftest import qipy_action
from qitest.test.conftest import qitest_action


def test_finding_qi_python_modules(qipy_action, qibuild_action, qitest_action):
    """ Test Finding Qi Python Modules """
    qipy_action.add_test_project("foomodules")
    # Need to have qibuild inside the virtualenv for
    # qipy run -- qitest run to work
    this_dir = os.path.dirname(__file__)
    top_dir = os.path.join(this_dir, "..", "..", "..")
    qipy_action.worktree.add_project(top_dir)
    # Hack to make the worktree inside qibuild_action aware
    # that there are python projects registered
    worktree = qibuild_action.build_worktree.worktree
    worktree.reload()
    project = qibuild_action.add_test_project("usefoopymodule")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    with qisys.sh.change_cwd(project.path):
        qibuild_action("configure")
        qipy_action("run", "--no-exec", "--", "qitest", "run")
