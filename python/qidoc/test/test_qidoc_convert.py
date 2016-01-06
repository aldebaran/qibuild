## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qidoc.test.conftest import TestDocWorkTree

def test_convert_from_qi2(qidoc_action):
    qidoc_action.add_test_project("qidoc2/with_src")
    qidoc_action("convert", "--all")
    doc_worktree = TestDocWorkTree()
    assert len(doc_worktree.doc_projects) == 3
