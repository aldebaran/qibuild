## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qisys.command
import qibuild.find

import pytest

def test_running_from_build_dir(qibuild_action):
    # Running `qibuild configure hello` `qibuild make hello` and running
    # the `hello` executable should work out of the box

    qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    hello = qibuild.find.find_bin([hello_proj.sdk_directory], "hello")
    qisys.command.call([hello])

def test_make_without_configure(qibuild_action):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.cmake_builder.NotConfigured):
        qibuild_action("make", "-s", "hello")


def test_running_from_build_dir_incremental(qibuild_action):
    qibuild_action.add_test_project("world")
    hello_proj = qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("make", "hello")
    hello = qibuild.find.find_bin([hello_proj.sdk_directory], "hello")
    qisys.command.call([hello])
