#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Parallel Builder """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.parallel_builder


class FakeProject(object):
    """ FakeProject Class """

    build_log = list()

    def __init__(self, name, deps=None):
        """ FakeProject Init """
        self.name = name
        self.build_type = "Debug"
        if deps:
            self.build_depends = deps
        else:
            self.build_depends = set()

    def build(self, *args, **kwargs):
        """ Build """
        self.build_log.append(self.name)


def is_before(mylist, a, b):
    """ Is Before """
    a_index = mylist.index(a)
    b_index = mylist.index(b)
    return a_index < b_index


def test_simple():
    """ Test Simple """
    a = FakeProject("a")
    b = FakeProject("b")
    c = FakeProject("c", deps=["a", "b"])
    builder = qibuild.parallel_builder.ParallelBuilder()
    builder.prepare_build_jobs([a, b, c])
    builder.build(num_workers=2)
    build_log = FakeProject.build_log
    assert is_before(build_log, "a", "c")
    assert is_before(build_log, "b", "c")
