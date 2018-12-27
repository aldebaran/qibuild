#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Foreach """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_simple(qibuild_action, record_messages):
    """ Test Simple """
    qibuild_action.add_test_project("nested")
    # only command we can be sure will always be there, even on cmd.exe :)
    qibuild_action("foreach", "--", "python", "--version")
    assert record_messages.find("nested")
    assert record_messages.find("nested/foo")
