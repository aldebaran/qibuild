#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Parallel """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import threading
import pytest

import qisys.parallel


def test_parallel_empty():
    """ Ensure that parallel does nothing with an empty iterator. """
    qisys.parallel.foreach([], pytest.fail, 0)
    qisys.parallel.foreach([], pytest.fail, 1)
    qisys.parallel.foreach([], pytest.fail, 4)


def test_parallel_result():
    """ Ensure that parallel does not change the result. """
    def sum_worker(n):
        """ Sum Worker """
        lock.acquire()
        result[0] += n
        lock.release()
    lock = threading.Lock()
    nums = [1, 2, 3, 4, 5]
    result = [0]
    qisys.parallel.foreach(nums, sum_worker)
    assert sum(nums) == result[0]
    result = [0]
    qisys.parallel.foreach(nums, sum_worker, 1)
    assert sum(nums) == result[0]
    result = [0]
    qisys.parallel.foreach(nums, sum_worker, 3)
    assert sum(nums) == result[0]
    result = [0]
    qisys.parallel.foreach(nums, sum_worker, 10)
    assert sum(nums) == result[0]
