""" Re-implementation of CTest in Python.

Necessary to by-pass some small ctest shortcomings.
"""

import os
import sys
import re
import shlex
import logging
import subprocess
import time
import threading

import qibuild

LOGGER = logging.getLogger(__name__)

class ProcessThread(threading.Thread):
    def __init__(self, test_name, cmd, cwd, env):
        threading.Thread.__init__(self, name="ProcessThread<%s>" % test_name)
        self.cmd = cmd
        self.cwd = cwd
        self.env = env
        self.out = ""
        self.process = None

    def run(self):
        self.process = subprocess.Popen(self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self.cwd,
            env=self.env)
        while self.process.poll() is None:
            self.out += self.process.stdout.readline()
            sys.stdout.write(".")
            sys.stdout.flush()



def run_test(build_dir, test_name, cmd, properties, build_env):
    """ Run a test. Return
    (res, output) where res is a boolean
    stating if the test was sucessul, and
    output is the output of the test

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
    process_thread = ProcessThread(test_name, cmd, build_dir, env)
    process_thread.start()
    process_thread.join(timeout)
    process = process_thread.process
    out = process_thread.out
    if process_thread.isAlive():
        process.terminate()
        return (False, out + "\n*** Timed out (%i s)\n" % timeout)
    else:
        return (process.returncode == 0, out)


def run_tests(build_dir, build_env):
    """ Called by toc.test_project

    Returns True if all test passed
    """
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
    return res


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

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir")
    args = parser.parse_args()
    build_dir = args.build_dir
    run_tests(build_dir)



if __name__ == "__main__":
    main()
