## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import json

def test_simple(qitest_action, tmpdir, record_messages):
    tests = [{"name" : "foo", "gtest" : True},
             {"name" : "test_bar"},
             {"name" : "test_baz", "pytest" : True}]
    qitest_json = tmpdir.join("qitest.json")
    qitest_json.write(json.dumps(tests))
    qitest_action("list", cwd=tmpdir.strpath)
    assert record_messages.find("foo.*\(invalid name\)")
    assert record_messages.find("test_bar.*\(no type\)")
