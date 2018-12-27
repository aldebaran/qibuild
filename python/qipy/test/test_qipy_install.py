#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_install(qipy_action, tmpdir):
    """ Test Install """
    _big_project = qipy_action.add_test_project("big_project")
    dest = tmpdir.join("dest")
    qipy_action("install", "big_project", dest.strpath)
    site_packages = dest.join("lib", "python2.7", "site-packages")
    assert site_packages.join("spam.py").check(file=True)
    assert site_packages.join("foo", "bar", "baz.py").check(file=True)
    assert dest.join("bin", "script.py").check(file=True)


def test_install_with_distutils(qipy_action, tmpdir):
    """ Test INstall With DistUtils """
    _with_distutils = qipy_action.add_test_project("with_distutils")
    dest = tmpdir.join("dest")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("install", "foo", dest.strpath)
    assert dest.join("bin", "foo").check(file=True)


def test_empty_install(qipy_action, tmpdir):
    """ Test Empty Install """
    _empty = qipy_action.add_test_project("empty")
    dest = tmpdir.join("dest")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    error = qipy_action("install", "empty", dest.strpath, raises=True)
    assert "Could not find anything to install" in error
