#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiTest Runner """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import re
import os
import json
import abc

import qitest.test_queue
from qisys import ui


class TestSuiteRunner(object):
    """ Interface for a class able to run a test suite """

    __metaclass__ = abc.ABCMeta

    def __init__(self, project):
        """ TestSuiteRunner Init """
        self.project = project
        self._patterns = list()
        self._excludes = list()
        self.num_jobs = 1
        self.repeat_until_fail = 0
        self.cwd = os.getcwd()
        self.env = None
        self.verbose = False
        self.perf = False
        self.nightly = False
        self.coverage = False
        self.nightmare = False
        self.test_output_dir = None
        self.capture = True
        self.last_failed = False
        self._tests = project.tests

    @abc.abstractproperty
    def launcher(self):
        """ This function should return a :py:class:`.TestLauncher` """
        pass

    def run(self):
        """
        Run all the tests.
        Return True if and only if the whole suite passed.
        """
        test_queue = qitest.test_queue.TestQueue(self.tests)
        test_queue.launcher = self.launcher
        test_queue.launcher.capture = self.capture
        ok = test_queue.run(num_jobs=self.num_jobs,
                            repeat_until_fail=self.repeat_until_fail)
        return ok

    @property
    def patterns(self):
        """ Patters Getter """
        return self._patterns

    @patterns.setter
    def patterns(self, value):
        """ Patters Setter """
        if value:
            # just checking regexps are valid
            _unused = [re.compile(x) for x in value]
        self._patterns = value

    @property
    def excludes(self):
        """ Excludes Getter """
        return self._excludes

    @excludes.setter
    def excludes(self, value):
        """ Excludes Setter """
        if value:
            # just checking regexps are valid
            _unused = [re.compile(x) for x in value]
        self._excludes = value

    @property
    def tests(self):
        """ Tests """
        res = [x for x in self._tests if
               match_patterns(self.patterns, x["name"], default=True)]
        res = [x for x in res if not
               match_patterns(self.excludes, x["name"], default=False)]
        # Perf tests are run alone
        res = [x for x in res if x.get("perf", False) == self.perf]
        # But nightly tests are run along with the normal tests
        if not self.nightly:
            res = [x for x in res if x.get("nightly", False) is False]
        if self.last_failed:
            failed_names = self.get_last_failed_names()
            res = [x for x in res if x["name"] in failed_names]
            if not res:
                ui.warning("No failing tests found")
        return res

    def get_last_failed_names(self):
        """ Return the list of the test names that failed during the previous run """
        path = self.launcher.project.sdk_directory
        fail_json = os.path.join(path, ".failed.json")
        names = list()
        if not os.path.exists(fail_json):
            return names
        with open(fail_json, "r") as fp:
            names = json.load(fp)
        return names


class TestLauncher(object):
    """ Interface for a class able to launch a test. """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """ Set by the test suite, the launcher may need to know about its worker index """
        self.worker_index = None
        self.capture = True

    @abc.abstractmethod
    def launch(self, test):
        """ Should return a :py:class:`.TestResult` """
        pass


def match_patterns(patterns, name, default=True):
    """ Retur True if Match Patterns """
    if not patterns:
        return default
    for pattern in patterns:
        res = re.search(pattern, name)
        if res:
            return True
    return False
