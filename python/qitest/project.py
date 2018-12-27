#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiTest Project """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import qitest.conf


class TestProject(object):
    """ TestProject """

    def __init__(self, qitest_json):
        """ TestProject Init """
        self.name = None
        self.tests = qitest.conf.parse_tests(qitest_json)
        self.sdk_directory = os.path.dirname(qitest_json)
