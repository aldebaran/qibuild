## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qitoolchain.database
import qitoolchain.feed
import qitoolchain.qipackage

def test_feed(feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", "1.42")
    boost_package.url = "ftp://example.org/boost-1.42.zip"
    feed.add_package(boost_package)
    parser = qitoolchain.feed.ToolchainFeedParser("foo")
    parser.parse(feed.url)
    packages = parser.get_packages()
    assert packages[0].url == boost_package.url

def test_create_package_with_dependencies(toolchains):
    toolchains.create("foo")
    world_package = toolchains.add_package("foo", "world")
    hello_package = toolchains.add_package("foo", "hello", run_depends=["world"])
    toolchain = qitoolchain.get_toolchain("foo")
    actual = toolchain.solve_deps([hello_package], dep_types=["runtime"])
    assert actual == [world_package, hello_package]

def test_fake_ctc(fake_ctc):
    sysroot = fake_ctc.get_sysroot()
    assert os.path.exists(sysroot)
