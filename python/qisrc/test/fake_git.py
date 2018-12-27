#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Fake Git """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

from qisrc.test.conftest import FakeGit


def test_persistent_config():
    """ Test Persistent Config """
    git1 = FakeGit("repo")
    git1.set_config("foo.bar", 42)
    git2 = FakeGit("repo")
    assert git2.get_config("foo.bar") == 42
    assert git2.get_config("notset") is None


def test_fake_call():
    """ Test Fake Call """
    git = FakeGit("repo")
    git.add_result("fetch", 0, "")
    (retcode, _) = git.fetch(raises=False)
    assert retcode == 0
    git2 = FakeGit("repo2")
    git2.add_result("fetch", 2, "Remote end hung up unexpectedly")
    (retcode, out) = git2.fetch(raises=False)
    assert retcode == 2
    assert "Remote end hung up" in out


def test_wrong_setup():
    """ Test Wrong Setup """
    git = FakeGit("repo")
    git.add_result("checkout", 0, "")
    git.checkout("-f", "master")
    with pytest.raises(Exception) as e:
        git.fetch()
    assert "Unexpected call to fetch" in e.value.message


def test_configured_but_not_called_enough():
    """ Test Configured But Not Called Enough """
    git = FakeGit("repo")
    git.add_result("checkout", 0, "")
    git.add_result("checkout", 1, "Unstaged changes")
    git.checkout("next")
    with pytest.raises(Exception) as e:
        git.check()
    assert "checkout was configured to be called 2 times" in e.value.message
    assert "was only called 1 times" in e.value.message


def test_configured_but_not_called():
    """ Test Configured But Not Called """
    git = FakeGit("repo")
    git.add_result("checkout", 1, "")
    git.add_result("reset", 0, "")
    git.checkout(raises=False)
    with pytest.raises(Exception) as e:
        git.check()
    assert "reset was added as result but never called" in e.value.message


def test_commands_are_logged():
    """ Test Commands Are Logged """
    git = FakeGit("repo")
    git.add_result("fetch", 0, "")
    git.add_result("reset", 0, "")
    git.fetch()
    git.reset("--hard", quiet=True)
    calls = git.calls
    assert len(calls) == 2
    assert calls[0][0] == ("fetch",)
    assert calls[1][0] == ("reset", "--hard")
    assert calls[1][1] == {"quiet": True}
