## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisrc.test.conftest import git_server, qisrc_action

def test_info(qibuild_action, qisrc_action, git_server, record_messages):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    foo_project = qibuild_action.create_project("foo")
    record_messages.reset()
    qibuild_action("info", "foo")
    assert record_messages.find("src: foo")
    assert record_messages.find("repo: foo.git")
    qibuild_action.chdir(foo_project.path)
    record_messages.reset()
    qibuild_action("info")
    assert record_messages.find("Build project: foo")
