## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

class TestResult:
    """ Just a small class to store the results for a test

    The ``error`` attribute is special. If set to True, it will
    cause TestSuiteRunner.run() to raise instead of simply returning
    False.

    Example include:

        * There was a Python exception in the threads spawned
          by the TestQueue

        * A dependency library was not found

    In both cases, the problem is in the build system and not the test
    itself, that' s why we have to raise

    The ``message`` is a list that will be sent to ``ui.info``. This
    allows test runners to have better control on console output
    """
    def __init__(self, test):
        self.test = test
        self.time = 0
        self.ok = False
        self.message = list()
        self.error = False
