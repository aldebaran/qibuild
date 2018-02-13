# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import pytest

from qisrc.test.conftest import FakeGit


def test_persistent_config():
    git1 = FakeGit("repo")
    git1.set_config("foo.bar", 42)
    git2 = FakeGit("repo")
    assert git2.get_config("foo.bar") == 42
    assert git2.get_config("notset") is None


def test_fake_call():
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
    git = FakeGit("repo")
    git.add_result("checkout", 0, "")
    git.checkout("-f", "master")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        git.fetch()
    assert "Unexpected call to fetch" in e.value.message


def test_configured_but_not_called_enough():
    git = FakeGit("repo")
    git.add_result("checkout", 0, "")
    git.add_result("checkout", 1, "Unstaged changes")
    git.checkout("next")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        git.check()
    assert "checkout was configured to be called 2 times" in e.value.message
    assert "was only called 1 times" in e.value.message


def test_configured_but_not_called():
    git = FakeGit("repo")
    git.add_result("checkout", 1, "")
    git.add_result("reset", 0, "")
    # pylint: disable-msg=E1101
    git.checkout(raises=False)
    with pytest.raises(Exception) as e:
        git.check()
    assert "reset was added as result but never called" in e.value.message


def test_commands_are_logged():
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
