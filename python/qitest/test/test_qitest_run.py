## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import sys
import os
import json

import qisys.command
import qisys.error
import qibuild.find

from qisys.test.conftest import only_linux

import pytest

def test_simple_run(tmpdir, qitest_action):
    ls = qisys.command.find_program("ls")
    tests = [
            { "name": "ls", "cmd" : [ls], "timeout" : 1 }
    ]
    qitest_json = tmpdir.join("qitest.json")
    qitest_json.write(json.dumps(tests))
    qitest_action("run", cwd=tmpdir.strpath)

def test_repeat_until_fail(tmpdir, qitest_action):
    ls = qisys.command.find_program("ls")
    rm = qisys.command.find_program("rm")
    foo = tmpdir.join("foo")
    foo.write("this is foo\n")
    tests = [
            {"name" : "ls", "cmd" : [ls, foo.strpath], "timeout" : 1 },
            {"name" : "rm", "cmd" : [rm, foo.strpath], "timeout" : 1 },
    ]
    qitest_json = tmpdir.join("qitest.json")
    qitest_json.write(json.dumps(tests))
    rc = qitest_action("run", "--repeat-until-fail", "2",
                       cwd=tmpdir.strpath, retcode=True)
    assert rc != 0

def test_no_capture(tmpdir, qitest_action):
    if not sys.stdout.isatty():
        # The test will fail anyway
        return

    test_tty = tmpdir.join("test_tty.py")
    test_tty.write("""
import sys
if not sys.stdout.isatty():
    sys.exit("sys.stdout is not a tty")
""")

    tests = [
            { "name": "test_tty", "cmd" : [sys.executable, test_tty.strpath], "timeout" : 1 }
    ]
    qitest_json = tmpdir.join("qitest.json")
    qitest_json.write(json.dumps(tests))
    rc = qitest_action("run", "--no-capture",
                       cwd=tmpdir.strpath, retcode=True)
    assert rc == 0

def test_run_last_failed(tmpdir, qitest_action, record_messages):
    test_one = tmpdir.join("test_one.py")
    test_one.write("import sys; sys.exit(1)")
    test_two = tmpdir.join("test_two.py")
    test_two.write("")
    qitest_json = tmpdir.join("qitest.json")
    tests = [
              { "name": "test_one", "cmd" : [sys.executable, test_one.strpath], "timeout" : 1},
              { "name": "test_two", "cmd" : [sys.executable, test_two.strpath], "timeout" : 1},
           ]
    qitest_json.write(json.dumps(tests))
    qitest_action.chdir(tmpdir)
    qitest_action("run", retcode=True)
    record_messages.reset()
    qitest_action("run", "--last-failed", retcode=True)
    assert not record_messages.find("\(2/2\) test_two")
    assert record_messages.find("\(1/1\) test_one")
    test_one.write("")
    record_messages.reset()
    qitest_action("run", "--last-failed", retcode=True)
    qitest_action("run", "--last-failed", retcode=True)
    assert record_messages.find("No failing tests found")

def test_exclude(tmpdir, qitest_action):
    tests = [
      { "name" : "foo", "cmd" : [sys.executable, "--version"]},
      { "name" : "bar", "cmd" : [sys.executable , "-c", "import sys ; sys.exit(1)"]}
    ]
    qitest_json = tmpdir.join("qitest.json")
    qitest_json.write(json.dumps(tests))
    rc = qitest_action("run", "--exclude", "bar", cwd=tmpdir.strpath,
            retcode=True)
    assert rc == 0

def test_ignore_timeouts(qitest_action, tmpdir):
    qitest_json = tmpdir.join("qitest.json")
    sleep_cmd = qisys.command.find_program("sleep")
    qitest_json.write("""
[
 {"name": "test_one", "cmd" : ["%s", "2"], "timeout" : 1}
]
""" % sleep_cmd)
    rc = qitest_action("run", "--qitest-json", qitest_json.strpath, "--ignore-timeouts",
                       retcode=True)
    assert rc == 0

# Even though clang supports the --cov flag, gcovr does not seem
# to work on mac
@only_linux
def test_action_coverage(qibuild_action, qitest_action):
    gcovr = qisys.command.find_program("gcovr", raises=False)
    if not gcovr:
        return
    coverme_proj = qibuild_action.add_test_project("coverme")
    qibuild_action("configure", "coverme", "--coverage")
    qibuild_action("make", "coverme")
    qitest_action("run", "coverme", "--coverage", "--cov-exclude=NONE")
    xml = os.path.join(coverme_proj.sdk_directory, "coverage-results",
                       "coverme.xml")
    # Can't do more tests because by default gcovr is called
    # with --exclude *.test.*. See more low-level tests
    # in qibuild/test/test_coverage.py for more precise tests
    qisys.qixml.read(xml)


def test_when_missing_libs(qibuild_action, qitest_action):
    """ Sometimes the build system is broken and shared
    libraries dependencies cannnot be found. In this case,
    make sure ``qitest`` raises an exception instead
    of just having a non-zero return code,
    so that it's clear it's not just a failing test
    but something more serious

    """
    world_proj = qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    # Create a nasty bug:
    lib_world = qibuild.find.find_lib([world_proj.sdk_directory], "world",
                                     expect_one=True)
    os.remove(lib_world)
    qitest_action.chdir("hello")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qitest_action("run")
