#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from setuptools import setup

setup(
    name="hello",
    version="0.1",
    description="a test",
    url="https://example.com",
    py_modules=['hello'],
    entry_points={
        "console_scripts": [
            "hello = hello:main",
        ]
    }
)
