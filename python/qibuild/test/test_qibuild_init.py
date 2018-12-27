#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild Init """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

import qisys.script


def test_works_from_an_empty_dir(tmpdir, monkeypatch):
    """ Test Work From Empty Dir """
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qibuild.actions.init")
    assert tmpdir.join(".qi").check(dir=True)


def test_fails_if_qi_dir(tmpdir, monkeypatch):
    """ Test Fails If .qi in Dir """
    tmpdir.mkdir(".qi")
    monkeypatch.chdir(tmpdir)
    with pytest.raises(Exception) as err:
        qisys.script.run_action("qibuild.actions.init")
    assert ".qi directory" in str(err.value)
