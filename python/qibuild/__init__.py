#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" This module contains a few functions for running CMake and building projects. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

QIBUILD_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def stringify_env(env):
    """ convert each key value pairs to strings in env list"""
    return dict(((str(key), str(val)) for key, val in env.items()))
