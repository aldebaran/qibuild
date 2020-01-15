#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qidoc.test.conftest import TestDocWorkTree


def test_convert_from_qi2(qidoc_action):
    """ Test Convert From Qi 2 """
    qidoc_action.add_test_project("qidoc2/with_src")
    qidoc_action("convert", "--all")
    doc_worktree = TestDocWorkTree()
    assert len(doc_worktree.doc_projects) == 3
