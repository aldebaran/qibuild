#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest
import six

import qisys.sh
from qibuild.test.conftest import qibuild_action


@pytest.mark.skipif(six.PY3, reason="Only testable with python 2.7")
def test_simple(qipy_action):
    """ Test Simple """
    _a_project = qipy_action.add_test_project("a_lib")
    _big_project = qipy_action.add_test_project("big_project")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("run", "--no-exec", "--", "python", "-m", "a")
    qipy_action("run", "--no-exec", "--", "python", "-m", "foo.bar.baz")


@pytest.mark.skipif(six.PY3, reason="Only testable with python 2.7")
def test_cpp(qipy_action, qibuild_action):
    """ Test Cpp """
    qipy_action.add_test_project("c_swig")
    qibuild_action("configure", "swig_eggs")
    qibuild_action("make", "swig_eggs")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("run", "--no-exec", "--", "python", "-c", "import eggs")


@pytest.mark.skipif(six.PY3, reason="Only testable with python 2.7")
def test_with_deps(qipy_action):
    """ Test With Deps """
    qipy_action.add_test_project("with_deps")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("run", "--no-exec", "--", "python", "-c", "import markdown")


@pytest.mark.skipif(six.PY3, reason="Only testable with python 2.7")
def test_with_distutils(qipy_action):
    """ Test With DistUtils """
    qipy_action.add_test_project("with_distutils")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    qipy_action("run", "--no-exec", "foo")


@pytest.mark.skipif(six.PY3, reason="Only testable with python 2.7")
def test_qimodule(qipy_action):
    """ Test QiModule """
    qipy_action.add_test_project("foomodules")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    sourceme = qipy_action("sourceme")
    bin_path = os.path.dirname(sourceme)
    venv_path = os.path.join(bin_path, "..")
    venv_path = qisys.sh.to_native_path(venv_path)
    for name in ["foo", "bar"]:
        mod_path = os.path.join(venv_path, "share", "qi", "module", "%s.mod" % name)
        with open(mod_path, "r") as fp:
            contents = fp.read()
        assert contents == "python\n"


def test_fails_on_bad_requirements_txt(qipy_action):
    """ Test Fail On Bad Requirements Txt """
    a_project = qipy_action.add_test_project("a_lib")
    requirements_txt = os.path.join(a_project.path, "requirements.txt")
    with open(requirements_txt, "w") as fp:
        fp.write("no such package\n")
    rc = qipy_action("bootstrap", retcode=True)
    assert rc != 0
