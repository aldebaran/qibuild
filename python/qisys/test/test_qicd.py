## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import pytest
import qicd
import qisys.sh

from qisys.worktree import NoSuchProject
from qibuild.test.conftest import qibuild_action

def get_best_match(worktree, token):
    # qicd.find_best_match returns an absolute path,
    # this is used to simplify assertions
    res = qicd.find_best_match(worktree, token)
    if res:
        return qisys.sh.to_posix_path(os.path.relpath(res, worktree.root))

def test_matches_closest(worktree):
    worktree.create_project("agility/motion")
    worktree.create_project("apps/behaviors")
    worktree.create_project("apps/core")
    worktree.create_project("behavior")
    worktree.create_project("chuck")
    worktree.create_project("core/naoqicore")
    worktree.create_project("gui/choregraphe")
    worktree.create_project("lib/libalmath")
    worktree.create_project("lib/libalmathinternal")
    worktree.create_project("navigation")
    worktree.create_project("sdk/libnaoqi")
    worktree.create_project("tools/java")
    assert get_best_match(worktree, "behaviors") == "apps/behaviors"
    assert get_best_match(worktree, "naoqic") == "core/naoqicore"
    assert get_best_match(worktree, "libnao") == "sdk/libnaoqi"
    assert get_best_match(worktree, "chor") == "gui/choregraphe"
    assert get_best_match(worktree, "nav") == "navigation"
    assert get_best_match(worktree, "mathint") == "lib/libalmathinternal"
    assert get_best_match(worktree, "almathin") == "lib/libalmathinternal"
    assert get_best_match(worktree, "almath") == "lib/libalmath"

def test_qicd_dash_b(qibuild_action, record_messages):
    world_proj = qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    worktree = qibuild_action.build_worktree.worktree
    res = qicd.get_qibuild_path(worktree, "world")
    assert res == world_proj.path
    # pylint:disable-msg=E1101
    with pytest.raises(NoSuchProject) as e:
        qicd.get_qibuild_path(worktree, "worl")
