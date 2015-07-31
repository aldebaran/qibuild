## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisrc.git

def test_simple(git_server, qisrc_action, record_messages):
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_server.push_file("foo.git", "devel",
                         "this is devel\n", branch="devel",
                         message="start developing")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    record_messages.reset()
    qisrc_action("diff", "--all", "master")
    assert record_messages.find("devel | 1 +")
