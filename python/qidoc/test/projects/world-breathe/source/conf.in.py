#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
# FIXME: I don't know why but some tests fails with those imports
# from __future__ import absolute_import
# from __future__ import unicode_literals
# from __future__ import print_function

project = 'world'
master_doc = 'index'
extensions.append("breathe")
breathe_default_project = "libworld"
