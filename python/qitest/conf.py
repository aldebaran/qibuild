## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import argparse
import os
import json

def add_test(output, **kwargs):
    if not "name" in kwargs:
        raise Exception("Should provide a test name")
    if not "cmd" in kwargs:
        raise Exception("Should provide a test cmd")
    tests = list()
    if os.path.exists(output):
        with open(output, "r") as fp:
            tests = json.load(fp)
    name = kwargs["name"]

    test_names = dict((x["name"], x) for x in tests)
    matching_test = test_names.get(name)
    if matching_test:
        mess = "A test named '%s' already exists. (cmd=%s)" % (
            matching_test["name"], matching_test["cmd"])
        raise Exception(mess)

    tests.append(kwargs)
    with open(output, "w") as fp:
        json.dump(tests, fp, indent=2)

def parse_tests(conf_path):
    """ Parse the tests described in a qitest.json file.
    Returns a list of dictionaries

    """
    res = list()
    with open(conf_path, "r") as fp:
        res = json.load(fp)
    # Make sure environment is a dict string -> string
    for test in res:
        test_env = test.get("environment")
        if test_env:
            for key, value in test_env.iteritems():
                del test_env[key]
                test_env[key.encode("UTF-8")] = value.encode("UTF-8")
    return res

def write_tests(tests, conf_path, append=False):
    """ Write a list of tests to a config file
    """
    if append:
        if os.path.exists(conf_path):
            previous_tests = parse_tests(conf_path)
        else:
            previous_tests = list()
        tests = previous_tests + tests
    with open(conf_path, "w") as fp:
        return json.dump(tests, fp, indent=2)

def relocate_tests(project, tests):
    """ Make sure the tests can be relocated to the dest directory """
    new_tests = list()
    for test in tests:
        test["cmd"] = relocate_cmd(project, test["cmd"])
        new_tests.append(test)
    return new_tests

def relocate_cmd(project, cmd):
    """ Replace every absolute path by a relative path """
    new_cmd = list()
    for arg in cmd:
        if os.path.isabs(arg):
            relpath = os.path.relpath(arg, project.sdk_directory)
            if relpath.startswith(".."):
                # no choice but to keep it
                new_cmd.append(arg)
            else:
                new_cmd.append(relpath)
        else:
            new_cmd.append(arg)
    return new_cmd
