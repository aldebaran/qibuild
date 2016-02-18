## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
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

def test_keep_output_when_test_times_out(build_worktree):
    testme = build_worktree.add_test_project("testme")
    testme.configure()
    testme.build()
    testme.run_tests()
    test_dir = os.path.join(testme.sdk_directory, "test-results")
    timeout_xml = os.path.join(test_dir, "timeout.xml")
    tree = qisys.qixml.read(timeout_xml)
    test_cases = tree.findall("testsuite/testcase")
    assert len(test_cases) == 1
    test_case = test_cases[0]
    failure = test_case.find("failure")
    assert failure is not None
    assert failure.text == "timeout\n"
    assert failure.get("message") == "[TIMED OUT] (1s)"
