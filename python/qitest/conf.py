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
    with open(conf_path, "r") as fp:
        return json.load(fp)

def parse_qitest_cmake(qitest_cmake_path):
    tests = list()
    with open(qitest_cmake_path, "r") as fp:
        lines = fp.readlines()
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", nargs="+")
    parser.add_argument("--name", required=True)
    parser.add_argument("--gtest", action="store_true",
                        help="Tell qitest this is a test using gtest")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--nightly", action="store_true")
    parser.add_argument("--perf", action="store_true")
    parser.add_argument("--output", required=True)
    parser.add_argument("--working-directory")
    parser.set_defaults(nightly=False, perf=False)
    for line in lines:
        line = line.strip()
        args = parser.parse_args(args=line.split(";"))
        test = vars(args)
        tests.append(test)
    return tests

