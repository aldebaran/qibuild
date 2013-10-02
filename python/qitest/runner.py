import abc
import re
import os

import qitest.test_queue

class TestSuiteRunner(object):
    """ Interface for a class able to run a test suite """

    def __init__(self, tests):
        self.pattern = None
        self.num_jobs = 1
        self.cwd = os.getcwd()
        self.env = None
        self.verbose = False
        self._tests = tests

    @abc.abstractproperty
    def launcher(self):
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
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        if value:
            self._pattern = re.compile(value)
        else:
            self._pattern = None

    @property
    def tests(self):
        return [x for x in self._tests if match_pattern(self.pattern, x["name"])]

class TestLauncher(object):
    """ Interface for a class able to launch a test. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def launch(self, test):
        """ Should return a TestResult """
        pass


def match_pattern(pattern, name):
    if not pattern:
        return True
    try:
        res = re.search(pattern, name)
    except Exception as e:
        mess = "Invalid pattern \"{}\": {}".format(pattern, e)
        raise Exception(mess)
    return res
