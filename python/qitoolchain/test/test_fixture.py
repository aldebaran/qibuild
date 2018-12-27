#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Fixture """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qitoolchain.feed
import qitoolchain.database
import qitoolchain.qipackage


def test_feed(feed):
    """ Test Feed """
    boost_package = qitoolchain.qipackage.QiPackage("boost", "1.42")
    boost_package.url = "ftp://example.org/boost-1.42.zip"
    feed.add_package(boost_package)
    parser = qitoolchain.feed.ToolchainFeedParser("foo")
    parser.parse(feed.url)
    packages = parser.get_packages()
    assert packages[0].url == boost_package.url


def test_create_package_with_dependencies(toolchains):
    """ Test Create Package With Dependencies """
    toolchains.create("foo")
    world_package = toolchains.add_package("foo", "world")
    hello_package = toolchains.add_package("foo", "hello", run_depends=["world"])
    toolchain = qitoolchain.get_toolchain("foo")
    actual = toolchain.solve_deps([hello_package], dep_types=["runtime"])
    assert actual == [world_package, hello_package]


def test_fake_ctc(fake_ctc):
    """ Test Fake Cross Toolchain """
    assert os.path.exists(fake_ctc.get_sysroot())
