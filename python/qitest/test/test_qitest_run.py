## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import json

import qisys.command
import qibuild.find

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
