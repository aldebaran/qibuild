#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys

import qisys.command


def test_read_config(qipy_action):
    """ Test Read Config """
    big_project = qipy_action.add_test_project("big_project")
    scripts = big_project.scripts
    assert len(scripts) == 1
    script = scripts[0]
    assert script.src == "bin/script.py"
    modules = big_project.modules
    assert len(modules) == 1
    spam = modules[0]
    assert spam.src == ""
    assert spam.name == "spam"
    packages = big_project.packages
    assert len(packages) == 1
    foo1 = packages[0]
    assert foo1.src == "lib"
    assert foo1.name == "foo"
    assert big_project.python_path == [
        big_project.path,
        os.path.join(big_project.path, "lib")
    ]


def test_install(qipy_action, tmpdir):
    """ Test Install """
    big_project = qipy_action.add_test_project("big_project")
    dest = tmpdir.join("dest")
    big_project.install(dest.strpath)
    assert dest.join("bin", "script.py").check(file=True)
    site_packages = dest.join("lib", "python2.7", "site-packages")
    assert site_packages.join("foo", "__init__.py").check(file=True)
    assert site_packages.join("foo", "bar", "baz.py").check(file=True)


def test_run(qipy_action):
    """ Test Run """
    # can't use `qipy run` here because it will call os.execv and
    # screw other tests
    big_project = qipy_action.add_test_project("big_project")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.pathsep.join(big_project.python_path)
    script = os.path.join(big_project.path, "bin", "script.py")
    cmd = [sys.executable, script]
    qisys.command.call(cmd, env=env)


def test_qimodule(qipy_action):
    """ Test QiModule """
    foomodule_proj = qipy_action.add_test_project("foomodules")
    module = foomodule_proj.modules[0]
    assert module.qimodule
    package = foomodule_proj.packages[0]
    assert package.qimodule
