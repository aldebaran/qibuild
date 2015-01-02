## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qitoolchain.toolchain
import qitoolchain.svn_package

from qisrc.test.conftest import svn_server

def test_svn_update(svn_server, feed, toolchains):
    boost_url = svn_server.create_repo("boost")
    svn_server.commit_file("boost", "version.hpp", '#define BOOST_VERSION "1_55"\n')
    boost_package = qitoolchain.svn_package.SvnPackage("boost")
    boost_package.url = boost_url
    feed.add_svn_package(boost_package)
    toolchain = qitoolchain.toolchain.Toolchain("foo")
    toolchain.update(feed.url)
    boost_path = toolchain.get_package("boost").path
    version_hpp = os.path.join(boost_path, "version.hpp")
    with open(version_hpp, "r") as fp:
        assert fp.read() ==  '#define BOOST_VERSION "1_55"\n'
    svn_server.commit_file("boost", "version.hpp", '#define BOOST_VERSION "1_56"\n')
    toolchain.update(feed.url)
    with open(version_hpp, "r") as fp:
        assert fp.read() ==  '#define BOOST_VERSION "1_56"\n'
