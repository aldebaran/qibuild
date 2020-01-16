#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiToolchain SVN Status """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qitoolchain.toolchain
import qitoolchain.svn_package
from qitoolchain.test.conftest import qitoolchain_action
from qibuild.test.conftest import record_messages
from qisrc.test.conftest import svn_server


def test_simple(qitoolchain_action, svn_server, feed, record_messages):
    """ Test Simple """
    toolchain = qitoolchain.toolchain.Toolchain("foo")
    boost_url = svn_server.create_repo("boost")
    svn_server.commit_file("boost", "version.hpp", "")
    qt_url = svn_server.create_repo("qt")
    boost_package = qitoolchain.svn_package.SvnPackage("boost")
    boost_package.url = boost_url
    qt_package = qitoolchain.svn_package.SvnPackage("qt")
    qt_package.url = qt_url
    feed.add_svn_package(boost_package)
    feed.add_svn_package(qt_package)
    toolchain.update(feed.url)
    record_messages.reset()
    rc = qitoolchain_action("svn-status", "foo", retcode=True)
    assert rc == 0
    assert not record_messages.find("qt")
    assert not record_messages.find("boost")
    assert record_messages.find("All OK")
    # Now create a problem in the svn repo:
    boost_path = toolchain.get_package("boost").path
    version_hpp = os.path.join(boost_path, "version.hpp")
    os.remove(version_hpp)
    record_messages.reset()
    rc = qitoolchain_action("svn-status", "foo", retcode=True)
    assert rc != 0
    assert record_messages.find("boost")
    assert record_messages.find("version.hpp")
