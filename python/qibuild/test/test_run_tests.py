## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import qisys.qixml

def test_run(build_worktree):
    testme = build_worktree.add_test_project("testme")
    testme.configure()
    testme.build()
    ok = testme.run_tests()
    assert not ok
    test_dir = os.path.join(testme.sdk_directory, "test-results")
    xml_files = os.listdir(test_dir)
    xml_files = [x for x in xml_files if x.endswith(".xml")]
    for xml_file in xml_files:
        full_path = os.path.join(test_dir, xml_file)
        qisys.qixml.read(full_path)
