# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import os


def test_simple(qidoc_action):
    world_proj = qidoc_action.add_test_project("world")
    build_dir = os.path.join(world_proj.path, "build-doc")
    assert not os.path.exists(build_dir)
    qidoc_action("build", "world")
    assert os.path.exists(build_dir)
    qidoc_action("clean", "world")
    assert os.path.exists(build_dir)
    qidoc_action("clean", "world", "--force")
    assert not os.path.exists(build_dir)
