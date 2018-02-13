# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import threading

import pytest

import qisys.parallel


def test_parallel_empty():
    """Ensure that parallel does nothing with an empty iterator."""
    # pylint:disable-msg=E1101
    qisys.parallel.foreach([], pytest.fail, 0)
    # pylint:disable-msg=E1101
    qisys.parallel.foreach([], pytest.fail, 1)
    # pylint:disable-msg=E1101
    qisys.parallel.foreach([], pytest.fail, 4)


def test_parallel_result():
    """Ensure that parallel does not change the result."""

    def sum_worker(n):
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
