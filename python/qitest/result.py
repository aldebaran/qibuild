## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

class TestResult:
    """ Just a small class to store the results for a test

    """
    def __init__(self, test):
        self.test = test
        self.time = 0
        self.ok = False
        self.message = list()
