#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiBuild SourceMe """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import subprocess


def test_qibuild_sourceme(tmpdir, qibuild_action):
    """ Test QiBuild SourceMe """
    foo_proj = qibuild_action.create_project("foo")
    if not sys.platform.startswith("linux"):
        return
    print_env = tmpdir.join("print_env.py")
    print_env.write("""\
import os
for line in os.environ["LD_LIBRARY_PATH"].split():
    print(line)
""")
    sourceme = qibuild_action("sourceme")
    process = subprocess.Popen(". %s && python %s" % (sourceme, print_env.strpath),
                               shell=True, stdout=subprocess.PIPE)
    out, err = process.communicate()
    assert not err
    lines = out.splitlines()
    assert os.path.join(foo_proj.sdk_directory, "lib") in lines
