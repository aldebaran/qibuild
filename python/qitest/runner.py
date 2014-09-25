import abc
import re
import os

import qitest.test_queue

class TestSuiteRunner(object):
    """ Interface for a class able to run a test suite """

    def __init__(self, project):
        self.project = project
        self.pattern = None
        self.num_jobs = 1
        self.cwd = os.getcwd()
        self.env = None
        self.verbose = False
        self.perf = False
        self.nightly = False
        self.coverage = False
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
        res = [x for x in self._tests if match_pattern(self.pattern, x["name"])]
        # Perf tests are run alone
        res = [x for x in res if x.get("perf", False) == self.perf]
        # But nightly tests are run along with the normal tests
        if not self.nightly:
            res = [x for x in res if x.get("nightly", False) is False]
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


def match_pattern(pattern, name):
    if not pattern:
        return True
    try:
        res = re.search(pattern, name)
    except Exception as e:
        mess = "Invalid pattern \"{}\": {}".format(pattern, e)
        raise Exception(mess)
    return res
