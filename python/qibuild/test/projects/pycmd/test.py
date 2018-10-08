#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

print(", ".join([x.capitalize() for x in sys.argv[1:]]) + "!")
