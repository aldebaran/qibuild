## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
def test_simple(qibuild_action, record_messages):
    qibuild_action.add_test_project("nested")
    # only command we can be sure will always be there, even on
    # cmd.exe :)
    qibuild_action("foreach", "--", "python", "--version")
    assert record_messages.find("nested")
    assert record_messages.find("nested/foo")
