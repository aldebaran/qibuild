import re
import os

from qisys import ui
import qisys.command
import qitest.launcher
import qitest.test_queue

class TestSuiteRunner(object):
    def __init__(self, tests):
        self.num_jobs = 1
        self.cwd = os.getcwd()
        self.env = None
        self.verbose = False
        self.perf = False
        self.nightly = False
        self._tests = tests
        self._pattern = None
        self._coverage = False
        self._valgrind = False
        self._num_cpus = -1

    @property
    def tests(self):
        res =  list()
        res = [x for x in self._tests if match_pattern(self.pattern, x["name"])]
        res = [x for x in res if x.get("perf", False) == self.perf]
        res = [x for x in res if x.get("nightly", False) == self.nightly]
        return res

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
    def num_cpus(self):
        return self._num_cpus

    @num_cpus.setter
    def num_cpus(self, value):
        if value == -1:
            return
        if not qisys.command.find_program("taskset"):
            mess = "taskset was not found on the system.\n"
            mess += "Cannot set number of CPUs used by the tests"
            raise Exception(mess)

    @property
    def valgrind(self):
        return self._valgrind

    @valgrind.setter
    def valgrind(self, value):
        if not value:
            return
        if not qisys.command.find_program("valgrind"):
            raise Exception("valgrind was not found on the system")

    @property
    def coverage(self):
        return self._coverage

    @coverage.setter
    def coverage(self, value):
        if not qisys.command.find_program("gcovr"):
            raise Exception("please install gcovr in order to measure coverage")

    def run(self):
        """ Run all the tests.
        Return True if and only if the whole suite passed.

        """
        test_queue = qitest.test_queue.TestQueue(self.tests)
        launcher = qitest.launcher.ProcessTestLauncher(self)
        test_queue.launcher = launcher
        ok = test_queue.run(num_jobs=self.num_jobs)
        return ok


def match_pattern(pattern, name):
    if not pattern:
        return True
    try:
        res = re.search(pattern, name)
    except Exception as e:
        mess = "Invalid pattern \"{}\": {}".format(pattern, e)
        raise Exception(mess)
    return res
