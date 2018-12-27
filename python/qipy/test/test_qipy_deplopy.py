#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qibuild.test.test_qibuild_deploy import get_ssh_url


def test_simple(qipy_action, tmpdir):
    """ Test Simple """
    url = get_ssh_url(tmpdir)
    qipy_action.add_test_project("a_lib")
    qipy_action("deploy", "a", "--url", url)
    assert tmpdir.join("lib", "python2.7", "site-packages", "a.py").check(file=True)
