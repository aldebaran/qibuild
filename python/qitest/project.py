## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import qitest.conf

class TestProject():
    def __init__(self, qitest_json):
        self.name = None
        self.tests = qitest.conf.parse_tests(qitest_json)
        self.sdk_directory = os.path.dirname(qitest_json)
