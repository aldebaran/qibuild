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


