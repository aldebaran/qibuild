#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test DyLibs """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

import qibuild.dylibs


def test_create_symlinks_to_deps(tmpdir):
    """ Test Create Cimlinks To Deps """
    if sys.platform != 'darwin':
        return
    gtest_sdk = tmpdir.ensure("gtest/sdk", dir=True)
    lib_gtest = tmpdir.ensure("gtest/sdk/lib/libgtest.dylib", file=True)
    foo_sdk = tmpdir.ensure("foo/sdk", dir=True)
    _lib_foo = tmpdir.ensure("foo/sdk/lib/libfoo.dylib", file=True)
    qibuild.dylibs.fix_dylibs(foo_sdk.strpath, [gtest_sdk.strpath])
    foo_gtest_symlink = foo_sdk.join("lib/libgtest.dylib")
    pointee = foo_gtest_symlink.readlink()
    assert pointee == lib_gtest


def test_do_not_create_recursive_symlinks(tmpdir):
    """ Test Do Not Create Recursive SymLinks """
    if sys.platform != 'darwin':
        return
    gtest_sdk = tmpdir.ensure("gtest/sdk", dir=True)
    lib_gtest = tmpdir.ensure("gtest/sdk/lib/libgtest.dylib", file=True)
    foo_sdk = tmpdir.ensure("foo/sdk", dir=True)
    _lib_foo = tmpdir.ensure("foo/sdk/lib/libfoo.dylib", file=True)
    bar_sdk = tmpdir.ensure("bar/sdk", dir=True)
    _lib_bar = tmpdir.ensure("bar/sdk/lib/libbar.dylib", file=True)
    qibuild.dylibs.fix_dylibs(foo_sdk.strpath, [gtest_sdk.strpath])
    qibuild.dylibs.fix_dylibs(bar_sdk.strpath, [gtest_sdk.strpath, foo_sdk.strpath])
    bar_gtest_symlink = bar_sdk.join("lib/libgtest.dylib")
    pointee = bar_gtest_symlink.readlink()
    assert pointee == lib_gtest
