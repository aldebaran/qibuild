""" Re-implementation of CTest in Python.

Necessary to by-pass some small ctest shortcomings.
"""

import os
import sys
import re
import errno
import signal
import shlex
import logging
from xml.etree import ElementTree

import qibuild

LOGGER = logging.getLogger(__name__)

def _str_from_signal(code):
    """ Returns a nice string describing the signal

    """
    if code == signal.SIGSEGV:
        return "Segmentation fault"
    if code == signal.SIGABRT:
        return "Aborted"
    else:
        return "%i" % code

def run_test(build_dir, test_name, cmd, properties, build_env):
    """ Run a test. Return
    (res, output) where res is a string describing wether
    the test was sucessul, and output is the output of the test

    """

    timeout = properties.get("TIMEOUT")
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
    process_thread = qibuild.command.ProcessThread(cmd,
        name=test_name,
        cwd=build_dir,
        env=env)

    process_thread.start()
    process_thread.join(timeout)
    process = process_thread.process
    if not process:
        exception = process_thread.exception
        mess  = "Could not run test: %s\n" % test_name
        mess += "Error was: %s\n" % exception
        mess += "Full command was: %s\n" % " ".join(cmd)
        if isinstance(exception, OSError):
            if exception.errno == errno.ENOENT:
                mess += "Are you sure you have built the tests?"
        raise Exception(mess)
    out = process_thread.out
    if process_thread.isAlive():
        process.terminate()
        return (False,
            "%s\n*** Timed out (%i s)\n" % (out, timeout))
    else:
        retcode = process.returncode
        if retcode == 0:
            return(True, out)
        else:
            if retcode > 0:
                return(False,
                    "%s\n*** Return code: %i\n" % (out, retcode))
            else:
                desc = _str_from_signal(-retcode)
                return(False,
                    "%s\n*** %s\n" % (out, desc))


def run_tests(project, build_env):
    """ Called by toc.test_project

    Returns True if all test passed
    """
    build_dir = project.build_directory
    results_dir = os.path.join(project.directory, "build-tests",
        "results")
    tests = list()
    parse_ctest_test_files(tests, build_dir, list())
    res = True
    for (i, test) in enumerate(tests):
        (test_name, cmd, properties) = test
        sys.stdout.write("Running %i/%i %s ... " % (i+1, len(tests), test_name))
        sys.stdout.flush()
        (ok, out) = run_test(build_dir, test_name, cmd, properties, build_env)
        if ok:
            sys.stdout.write("[OK]\n")
        else:
            res = False
            sys.stdout.write("[FAIL]\n")
            print out
        xml_out = os.path.join(results_dir, test_name + ".xml")
        if not os.path.exists(xml_out):
            write_xml(xml_out, test_name, ok, out)
    return res


def write_xml(xml_out, test_name, ok, out):
    """ Write a XUnit XML file

    """
    to_write = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites tests="1" failures="{num_failures}" disabled="0" errors="0" time="0" name="All">
    <testsuite name="{testsuite_name}" tests="1" failures="{num_failures}" disabled="0" errors="0" time="0">
    <testcase name="{testcase_name}" status="run">
      {failure}
    </testcase>
  </testsuite>
</testsuites>
"""
    if ok:
        num_failures="0"
        failure = ""
    else:
        num_failures="1"
        failure = """
      <failure>
          <![CDATA[ {out} ]]>
    </failure>
"""
        failure = failure.format(out=out)
    to_write = to_write.format(num_failures=num_failures,
                               testsuite_name=test_name,
                               testcase_name=test_name,
                               failure=failure)
    qibuild.sh.mkdir(os.path.dirname(xml_out), recursive=True)
    with open(xml_out, "w") as fp:
        fp.write(to_write)

def parse_ctest_test_files(tests, root, subdirs):
    """ Recursively parse CTestTestfile.cmake,
    filling up the tests and subdirs lists passed as first
    argument

    """
    ctest_test_file = os.path.join(root, "CTestTestfile.cmake")
    with open(ctest_test_file, "r") as fp:
        lines = fp.readlines()
    cur_test = None
    cur_cmd = None
    for line in lines:
        match = re.match("SUBDIRS\((.*)\)", line)
        if match:
            subdir = match.groups()[0]
            subdirs.append(subdir)
        match = re.match("ADD_TEST\((\w+) (.*)\)", line)
        if match:
            groups = match.groups()
            cur_test = groups[0]
            args = groups[1]
            cur_cmd = shlex.split(args)
        match = re.match("SET_TESTS_PROPERTIES\((\w+) PROPERTIES (.*)\)", line)
        if match:
            groups = match.groups()
            test_name = groups[0]
            if test_name != cur_test:
                mess  = "Could not parse %s\n", ctest_test_file
                mess += "ADD_TEST was called with '%s'\n" % cur_test
                mess +="but SET_TESTS_PROPERTIES was called with '%s'\n" % test_name
                raise Exception(mess)
            properties = groups[1]
            properties = shlex.split(properties)
            test_properties = dict()
            for i in range(0, len(properties)/2):
                key = properties[2*i]
                value = properties[2*i+1]
                test_properties[key] = value
            tests.append((cur_test, cur_cmd, test_properties))
            cur_cmd = None
            cur_test = None

    for subdir in subdirs:
        new_root = os.path.join(root, subdir)
        parse_ctest_test_files(tests, new_root, list())



def test_parse():
    """ Just a quick test.
    Put it in a unittest test case looks a bit overkill

    """
    with qibuild.sh.TempDir() as tmp:
        build_dir = os.path.join(tmp, "build")
        os.mkdir(build_dir)
        ctest_test_file = os.path.join(build_dir, "CTestTestfile.cmake")
        with open(ctest_test_file, "w") as fp:
            fp.write(""" # CMake generated Testfile ...
# ...
# ...
SUBDIRS(a)
ADD_TEST(test_root "path/to/test_root")
SET_TESTS_PROPERTIES(test_root PROPERTIES TIMEOUT "20" ENVIRONMENT "SPAM=EGGS")
""")

        a = os.path.join(build_dir, "a")
        os.mkdir(a)
        a_ctest_test_file = os.path.join(a, "CTestTestfile.cmake")
        with open(a_ctest_test_file, "w") as fp:
            fp.write(""" # CMake generate Testfile ...
# ...
# ...
ADD_TEST(a_gtest "/path/to/a_gtest" "--gtest_output=xml:/path/to/a.xml")
SET_TESTS_PROPERTIES(a_gtest PROPERTIES TIMEOUT "20")
""")
        tests = list()
        subdirs = list()
        parse_ctest_test_files(tests, build_dir, subdirs)
        print tests


