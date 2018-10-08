#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qipy.test.conftest import *
from qisys.test.conftest import *
from qitoolchain.test.conftest import *
from qibuild.test.conftest import QiBuildAction


class QiPkgAction(TestAction):
    """ QiPkgAction Class """

    def __init__(self):
        """ QiPkgAction Init """
        super(QiPkgAction, self).__init__("qipkg.actions")

    def add_test_project(self, src):
        """ Add Test Project """
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.worktree.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)
        worktree_project = self.worktree.add_project(src)
        return worktree_project


@pytest.fixture
def qipkg_action(cd_to_tmpdir):
    """ QiPkg Action """
    return QiPkgAction()
