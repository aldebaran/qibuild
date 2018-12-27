#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Get Licences """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.config


def test_get_licenses(qibuild_action, toolchains):
    """ Test Get Licences """
    hello_proj = qibuild_action.create_project("hello", build_depends=["boost"])
    hello_proj.license = "proprietary"
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    boost_package = toolchains.add_package("foo", "boost")
    boost_package.license = "BSD"
    licenses = qibuild_action("get-licenses", "--config", "foo", "hello")
    assert licenses == {"hello": "proprietary", "boost": "BSD"}
    licenses = qibuild_action("get-licenses", "--config", "foo", "hello", "--oss")
    assert licenses == {"boost": "BSD"}
