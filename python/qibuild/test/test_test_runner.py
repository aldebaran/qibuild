#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Tes Runner """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qibuild.test_runner import get_cpu_list


def test_get_cpu_list():
    """ Test CPU List """
    # 4 cpus, 2 cpus per test, -j 2:
    worker_1_opts = get_cpu_list(4, 2, 0)
    worker_2_opts = get_cpu_list(4, 2, 1)
    assert worker_1_opts == [0, 1]
    assert worker_2_opts == [2, 3]
    # 2 cpus, 2 cpus per test, -j 2:
    worker_1_opts = get_cpu_list(2, 2, 0)
    worker_2_opts = get_cpu_list(2, 2, 1)
    assert worker_1_opts == [0, 1]
    assert worker_2_opts == [0, 1]
    # 8 cpus, 3 cpus per test, -j 3:
    worker_1_opts = get_cpu_list(8, 3, 0)
    worker_2_opts = get_cpu_list(8, 3, 1)
    worker_3_opts = get_cpu_list(8, 3, 2)
    assert worker_1_opts == [0, 1, 2]
    assert worker_2_opts == [3, 4, 5]
    assert worker_3_opts == [6, 7, 0]
