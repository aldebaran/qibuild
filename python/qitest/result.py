#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiTest Result """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


class TestResult(object):
    """ Just a small class to store the results for a test """

    def __init__(self, test):
        """ TestResult Init """
        self.test = test
        self.time = 0
        self.ok = False
        self.message = list()
