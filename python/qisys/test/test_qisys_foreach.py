## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

def test_qisys_foreach(qisys_action, record_messages):
    worktree = qisys_action.worktree
    tmpdir = worktree.tmpdir
    a_project = worktree.create_project("a_proj")
    a_path = tmpdir.join("a_proj")
    a_path.join("qiproject.xml").write("""
<project format="3">
  <project src="b_proj" />
</project>
""")
    b_proj = a_path.mkdir("b_proj")

    qisys_action("foreach", "ls")
    assert record_messages.find("a_proj")
    assert record_messages.find("a_proj/b_proj")
