#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest

import qipy.worktree
import qisys
from qisys.test.conftest import *  # pylint:disable=W0401,W0614


class QiPyAction(TestAction):
    """ QiPyAction Class """

    def __init__(self):
        """ QiPyAction Init """
        super(QiPyAction, self).__init__("qipy.actions")

    def add_test_project(self, src):
        """ Add Test Project """
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.worktree.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)
        worktree_project = self.worktree.add_project(src)
        python_project = qipy.worktree.new_python_project(self.worktree, worktree_project)
        return python_project


@pytest.fixture
def qipy_action(cd_to_tmpdir):
    """ QiPy Action """
    return QiPyAction()
