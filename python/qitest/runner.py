## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import abc
import re
import os

from qisys import ui
import qitest.test_queue

class TestSuiteRunner(object):
    """ Interface for a class able to run a test suite """

    def __init__(self, project):
        self.project = project
        self._patterns = list()
        self.num_jobs = 1
        self.cwd = os.getcwd()
        self.env = None
        self.verbose = False
        self.perf = False
        self.nightly = False
        self.coverage = False
        self.nightmare = False
        self.root_output_dir = None
        self._tests = project.tests

    @abc.abstractproperty
    def launcher(self):
        """ This function should return a :py:class:`.TestLauncher`

        """
        pass

    def run(self):
        """ Run all the tests.
        Return True if and only if the whole suite passed.

        """
        test_queue = qitest.test_queue.TestQueue(self.tests)
        test_queue.launcher = self.launcher
        ok = test_queue.run(num_jobs=self.num_jobs)
        return ok

    @property
    def patterns(self):
        return self._patterns

    @patterns.setter
    def patterns(self, value):
        if value:
            [re.compile(x) for x in value] # just checking regexps are valid
        self._patterns = value

    @property
    def tests(self):
        res = [x for x in self._tests if match_patterns(self.patterns, x["name"])]
        # Perf tests are run alone
        res = [x for x in res if x.get("perf", False) == self.perf]
        # But nightly tests are run along with the normal tests
        if not self.nightly:
            res = [x for x in res if x.get("nightly", False) is False]
        if not res and self.patterns:
            ui.error("No test found matching pattern")
        return res


class TestLauncher(object):
    """ Interface for a class able to launch a test. """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        # Set by the test suite, the launcher may need to know about its woker
        # index
        self.worker_index = None

    @abc.abstractmethod
    def launch(self, test):
        """ Should return a :py:class:`.TestResult` """
        pass


def match_patterns(patterns, name):
    if not patterns:
        return True
    for pattern in patterns:
        res = re.search(pattern, name)
        if res:
            return True
    return False
