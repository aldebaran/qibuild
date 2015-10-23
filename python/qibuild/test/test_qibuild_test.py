## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import sys
import platform

import xml.etree.ElementTree as etree

import qisys.worktree
import qibuild.worktree

from qitest.test.conftest import qitest_action

def test_various_outcomes(qibuild_action, record_messages):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qibuild_action("test", "testme", "-k", "ok")
    assert record_messages.find("All pass")
    record_messages.reset()

    rc = qibuild_action("test", "testme", "-k", "fail", retcode=True)
    assert record_messages.find("Return code: 1")
    assert rc == 1

    record_messages.reset()
    rc = qibuild_action("test", "testme", "-k", "segfault", retcode=True)
    if os.name == 'nt':
        assert record_messages.find("0xC0000005")
    else:
        assert record_messages.find("Segmentation fault")
    assert rc == 1

    record_messages.reset()
    rc = qibuild_action("test", "testme", "-k", "timeout", retcode=True)
    assert record_messages.find("Timed out")
    assert rc == 1

    rc = qibuild_action("test", "testme", "-k", "spam", retcode=True)
    result_dir = get_result_dir()
    assert "spam.xml" in os.listdir(result_dir)
    result = os.path.join(result_dir, "spam.xml")
    with open(result, "r") as f:
        assert len(f.read()) < 17000

    if qisys.command.find_program("valgrind"):
        # Test one file descriptor leak with --valgrind
        record_messages.reset()
        rc = qibuild_action("test", "testme", "-k", "fdleak","--valgrind", retcode=True)
        assert record_messages.find("file descriptor leaks: 1")
        assert rc == 1

        # Test for false positives with --valgrind
        record_messages.reset()
        rc = qibuild_action("test", "testme", "-k", "ok","--valgrind", retcode=True)
        assert not record_messages.find("file descriptor leaks")
        assert rc == 0

    rc = qibuild_action("test", "testme", "-k", "encoding", retcode=True)
    result_dir = get_result_dir()
    assert "encoding.xml" in os.listdir(result_dir)
    result = os.path.join(result_dir, "encoding.xml")
    with open(result, "r") as f:
        content = f.read()
    # Parsing XML shouldn't raise
    etree.parse(result)
    # Decode shouldn't raise
    if sys.platform.startswith("win"):
        assert "flag" in content.decode("ascii")
    else:
        assert "flag" in content.decode("utf-8")

def get_result_dir():
    worktree = qisys.worktree.WorkTree(os.getcwd())
    build_worktree = qibuild.worktree.BuildWorkTree(worktree)
    testme = build_worktree.get_build_project("testme")
    result_dir = os.path.join(testme.sdk_directory, "test-results")
    return result_dir

def test_do_not_overwrite_xml_when_test_fails(qibuild_action):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qibuild_action("test", "testme", "-k", "fake_gtest", retcode=True)
    testme_proj = qibuild_action.build_worktree.get_build_project("testme")
    fake_xml = os.path.join(testme_proj.sdk_directory, "test-results", "fake_gtest.xml")
    with open(fake_xml, "r") as fp:
        contents = fp.read()
    assert contents == "<gtest>FAKE_RESULTS</gtest>\n"

def test_setting_output_dir_with_project(qitest_action, qibuild_action, tmpdir):
    test_out = tmpdir.join("test-out", "testme")
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qitest_action("run", "testme", "-k", "ok", "--root-output-dir", test_out.strpath)
    ok_xml = test_out.join("testme", "test-results", "ok.xml")
    assert ok_xml.check(file=True)
    retcode = qitest_action("run", "testme", "-k", "fail",
                            "--root-output-dir", test_out.strpath,
                            retcode=True)
    assert not ok_xml.check(file=True)

def test_setting_output_dir_without_project(qitest_action, qibuild_action, tmpdir):
    dest = tmpdir.join("dest")
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qibuild_action("install", "--with-tests", "testme", dest.strpath)
    qitest_json = dest.join("qitest.json")
    out = tmpdir.join("out")
    qitest_action("run",
                  "-k", "ok",
                  "--qitest-json", qitest_json.strpath,
                  "--root-output-dir", out.strpath)
    assert out.join("test-results", "ok.xml").check(file=True)


def test_setting_build_prefix(qitest_action, qibuild_action, tmpdir):
    prefix = tmpdir.join("prefix")
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme", "--build-prefix", prefix.strpath)
    qibuild_action("make", "testme", "--build-prefix", prefix.strpath)
    qitest_action("run", "testme", "-k", "ok", "--build-prefix", prefix.strpath)
    test_results = prefix.join("build-sys-%s-%s" % (platform.system().lower(),
                               platform.machine().lower()),
                               "testme", "sdk", "test-results")
    assert test_results.join("ok.xml").check(file=True)
