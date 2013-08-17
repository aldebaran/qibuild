import re
from qisys import ui

class TestRunner(object):
    def __init__(self):
        self._tests = list()
        self._cwd = None
        self.env = None
        self._pattern = None
        self.verbose = False
        self.perf = False
        self.nightly = False
        self.coverage = False
        self.valgrind = False
        self.num_cpus = -1
        self.num_jobs = 1


    @property
    def tests(self):
        res =  [x for x in self._tests if match_pattern(self.pattern, x["name"])]
        return res

    @tests.setter
    def tests(self, value):
        self._tests = value

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        if value:
            self._pattern = re.compile(value)
        else:
            self._pattern = None

    def run(self):
        return True, (ui.green, "All pass. Congrats!")


def match_pattern(pattern, name):
    if not pattern:
        return True
    try:
        res = re.search(pattern, name)
    except Exception as e:
        mess = "Invalid pattern \"{}\": {}".format(pattern, e)
        raise Exception(mess)
    return res
