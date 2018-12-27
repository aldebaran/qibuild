#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Git Transaction """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


def test_transaction_success(mock_git):
    """ Test Transaction Success """
    mock_git.add_result("fetch", 0, "")
    mock_git.add_result("reset", 0, "")
    with mock_git.transaction() as transaction:
        mock_git.fetch()
        mock_git.reset("--hard")
    mock_git.check()
    assert transaction.ok


def test_transaction_fail(mock_git):
    """ Test Transaction Fail """
    mock_git.add_result("fetch", 0, "")
    mock_git.add_result("reset", 1, "no space left on device")
    with mock_git.transaction() as transaction:
        mock_git.fetch()
        mock_git.reset("--hard")
    mock_git.check()
    assert not transaction.ok
    assert "reset --hard" in transaction.output
    assert "no space left" in transaction.output


def test_transaction_stop_at_first_failure(mock_git):
    """ Test Transaction Stop At First Failure """
    mock_git.add_result("fetch", 1, "remote hung up on us")
    mock_git.add_result("reset", 0, "")
    with mock_git.transaction() as transaction:
        mock_git.fetch()
        mock_git.reset("--hard")
    assert not transaction.ok
    assert not mock_git.called("reset")
