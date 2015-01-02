## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
def test_no_cmake(qibuild_action, record_messages):
    qibuild_action.add_test_project("convert/no_cmake")
    qibuild_action.chdir("convert/no_cmake")
    qibuild_action("convert")
    assert record_messages.find("Would create")
    assert record_messages.find("--go")
    record_messages.reset()
    qibuild_action("convert", "--go")
    qibuild_action("configure")
    qibuild_action("make")

def test_pure_cmake(qibuild_action):
    qibuild_action.add_test_project("convert/pure_cmake")
    qibuild_action.chdir("convert/pure_cmake")
    qibuild_action("convert", "--go")
    qibuild_action("configure")

def test_qibuild2(qibuild_action, record_messages):
    qibuild_action.add_test_project("convert/qibuild2")
    qibuild_action.chdir("convert/qibuild2")
    qibuild_action("configure")
    qibuild_action("convert", "--go")
    qibuild_action("configure")
