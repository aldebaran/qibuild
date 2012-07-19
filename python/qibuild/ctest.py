## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Re-implementation of CTest in Python.

Necessary to by-pass some small ctest shortcomings.
"""

import os
import sys
import re
import datetime
import errno
import signal
import shlex

import qibuild
from qibuild import ui


def _str_from_signal(code):
    """ Returns a nice string describing the signal

    """
    if code == signal.SIGSEGV:
        return "Segmentation fault"
    if code == signal.SIGABRT:
        return "Aborted"
    else:
        return "%i" % code


class TestResult:
    """ Just a small class to store the results for a test

    """
    def __init__(self, test_name):
        self.test_name = test_name
        self.time = 0
        self.ok   = False
        # Output of the executable of the test
        self.out = ""
        # Short description of what went wrong
        self.message = ""


def run_test(build_dir, test_name, cmd, properties, build_env):
    """ Run a test.

    :return: (res, output) where res is a string describing wether
      the test was sucessul, and output is the output of the test

    """
    timeout = properties.get("TIMEOUT")
    if timeout:
        timeout = int(timeout)
    # we will merge the build env coming from toc
    # config with the env coming from CMake config,
    # assuming that cmake is always right
    env = build_env.copy()
    cmake_env = properties.get("ENVIRONMENT")
    if cmake_env:
        cmake_env = cmake_env.split(";")
        for key_value in cmake_env:
            key, value = key_value.split("=")
            env[key] = value
    working_dir = properties.get("WORKING_DIRECTORY")
    if working_dir:
        cwd=working_dir
    else:
        cwd=build_dir
    process_thread = qibuild.command.ProcessThread(cmd,
        name=test_name,
        cwd=cwd,
        env=env)

    res = TestResult(test_name)
    start = datetime.datetime.now()
    process_thread.start()
    process_thread.join(timeout)
    end = datetime.datetime.now()
    delta = end - start
    res.time = float(delta.microseconds) / 10**6 + delta.seconds

    process = process_thread.process
    if not process:
        exception = process_thread.exception
        mess  = "Could not run test: %s\n" % test_name
        mess += "Error was: %s\n" % exception
        mess += "Full command was: %s\n" % " ".join(cmd)
        if isinstance(exception, OSError):
            # pylint: disable-msg=E1101
            if exception.errno == errno.ENOENT:
                mess += "Are you sure you have built the tests?"
        raise Exception(mess)
    res.out = process_thread.out
    if process_thread.isAlive():
        process.terminate()
        res.ok = False
        res.message =  "Timed out (%i s)" % timeout
    else:
        retcode = process.returncode
        if retcode == 0:
            res.ok = True
        else:
            res.ok = False
            try:
                process.kill()
            except:
                pass
            if retcode > 0:
                res.message = "Return code: %i" % retcode
            else:
                res.message = _str_from_signal(-retcode)
    return res


def run_tests(project, build_env, pattern=None, slow=False, dry_run=False):
    """ Called by :py:meth:`qibuild.toc.Toc.test_project`

    :param test_name: If given, only run this test

    Always write some XML files in build-<config>/test-results
    (even if they were no tests to run at all)

    :return: a boolean to indicate if test was sucessful

    """
    build_dir = project.build_directory
    results_dir = os.path.join(project.build_directory, "test-results")

    all_tests = parse_ctest_test_files(build_dir)
    tests = list()
    slow_tests = list()
    if pattern:
        tests = [x for x in all_tests if re.search(pattern, x[0])]
        if not tests:
            mess  = "No tests matching %s\n" % pattern
            mess += "Known tests are:\n"
            for x in all_tests:
                mess += "  * " + x[0] + "\n"
            raise Exception(mess)
    else:
        for test in all_tests:
            (name, cmd_, properties) = test
            cost = properties.get("COST")
            if not slow and cost and float(cost) > 50:
                ui.debug("Skipping test", name, "because cost",
                         "(%s)"% cost, "is greater than 50")
                slow_tests.append(name)
                continue
            tests.append(test)

    if not tests:
        # Create a fake test result to keep CI jobs happy:
        fake_test_res = TestResult("compilation")
        fake_test_res.ok = True
        xml_out = os.path.join(results_dir, "compilation.xml")
        write_xml(xml_out, fake_test_res)
        ui.warning("No tests found for project", project.name)
        return

    if dry_run:
        ui.info(ui.green, "List of tests for", project.name)
        for (test_name, _, _) in tests:
            ui.info(ui.green, " * ", ui.reset, test_name)
        return

    ui.info(ui.green, "Testing", project.name, "...")
    ok = True
    fail_tests = list()
    for (i, test) in enumerate(tests):
        (test_name, cmd, properties) = test
        ui.info(ui.green, " * ", ui.reset, ui.bold,
                "(%2i/%2i)" % (i+1, len(tests)),
                ui.blue, test_name.ljust(25), end="")
        sys.stdout.flush()
        test_res = run_test(build_dir, test_name, cmd, properties, build_env)
        if test_res.ok:
            ui.info(ui.green, "[OK]")
        else:
            ok = False
            ui.info(ui.red, "[FAIL]")
            print test_res.out
            fail_tests.append(test_name)
        xml_out = os.path.join(results_dir, test_name + ".xml")
        if not os.path.exists(xml_out):
            write_xml(xml_out, test_res)


    if ok:
        ui.info("Ran %i tests" % len(tests))
        if slow_tests and not slow:
            ui.info("Note: %i" % len(slow_tests),
                    "slow tests did not run, use --slow to run them")
        ui.info("All pass. Congrats!")
        return True

    ui.error("Ran %i tests, %i failures" %
                  (len(tests), len(fail_tests)))
    for fail_test in fail_tests:
        ui.info(ui.bold, " -", ui.blue, fail_test)
    return False


def write_xml(xml_out, test_res):
    """ Write a XUnit XML file

    """
    to_write = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites tests="1" failures="{num_failures}" disabled="0" errors="0" time="{time}" name="All">
    <testsuite name="{testsuite_name}" tests="1" failures="{num_failures}" disabled="0" errors="0" time="{time}">
    <testcase name="{testcase_name}" status="run">
      {failure}
    </testcase>
  </testsuite>
</testsuites>
"""
    if test_res.ok:
        num_failures = "0"
        failure = ""
    else:
        num_failures = "1"
        failure = """
      <failure message="{message}">
          <![CDATA[ {out} ]]>
    </failure>
"""
        failure = failure.format(out=test_res.out,
            message=test_res.message)
    to_write = to_write.format(num_failures=num_failures,
                               testsuite_name="test", # nothing clever to put here :/
                               testcase_name=test_res.test_name,
                               failure=failure,
                               time=test_res.time)
    qibuild.sh.mkdir(os.path.dirname(xml_out), recursive=True)
    with open(xml_out, "w") as fp:
        fp.write(to_write)


def parse_ctest_test_files(build_dir):
    """ Recursively parse CTestTestfile.cmake.
    Returns a list of lists of 3 elements:
        [name, cmd, properties]

    """
    tests = list()
    subdirs = list()
    _parse_ctest_test_files(build_dir, tests, subdirs)
    return tests

def _parse_ctest_test_files(root, tests, subdirs):
    """ Helper for parse_ctest_test_files.
    We will fill up the tests and subdirs parameters as we go.

    """
    ctest_test_file = os.path.join(root, "CTestTestfile.cmake")
    if not os.path.exists(ctest_test_file):
        return list()
    with open(ctest_test_file, "r") as fp:
        lines = fp.readlines()

    current_test = None
    for i, line in enumerate(lines):
        match = re.match("SUBDIRS\((.*)\)", line)
        if match:
            subdir = match.groups()[0]
            subdirs.append(subdir)
            current_test = None
            continue
        match = re.match("ADD_TEST\(([a-zA-Z0-9_-]*) (.*)\)", line)
        if match:
            groups = match.groups()
            current_test = groups[0]
            args = groups[1]
            test_cmd = shlex.split(args)
            tests.append([current_test, test_cmd, dict()])
            continue
        match = re.match("SET_TESTS_PROPERTIES\(([a-zA-Z0-9_-]*) PROPERTIES (.*)\)", line)
        if match:
            groups = match.groups()
            if current_test is None:
                mess  = "Expecting ADD_TEST before SET_TESTS_PROPERTIES\n"
                mess += "in %s:%i" % (ctest_test_file, i+1)
                raise Exception(mess)
            name = groups[0]
            if name != current_test:
                mess  = "SET_TESTS_PROPERTIES called with wrong name\n"
                mess += "Expecting %s, got %s\n" % (current_test, name)
                mess += "in %s:%i" % (ctest_test_file, i+1)
                raise Exception(mess)
            properties = groups[1]
            properties = shlex.split(properties)
            test_properties = dict()
            for i in range(0, len(properties)/2):
                key = properties[2*i]
                value = properties[2*i+1]
                test_properties[key] = value
            # Just erase everything if there are two calls to set_test_properties()
            tests[-1][2] = test_properties
            current_test = None

    for subdir in subdirs:
        new_root = os.path.join(root, subdir)
        _parse_ctest_test_files(new_root, tests, list())
