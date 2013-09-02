""" Helper script to add a test to <build>/qitests.json """

import argparse
import json
import os


def add_test(output, name, cmd=None, timeout=None,
             nightly=False, perf=False):
    tests = list()
    if os.path.exists(output):
        with open(output, "r") as fp:
            tests = json.load(fp)

    new_test = {
        "name" : name,
        "cmd" : cmd,
    }
    if timeout:
        new_test["timeout"] = timeout
    if nightly:
        new_test["nightly"] = True
    if perf:
        new_test["perf"] = True

    tests.append(new_test)
    with open(output, "w") as fp:
        json.dump(tests, fp, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", nargs="+")
    parser.add_argument("--name", required=True)
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--nightly", action="store_true")
    parser.add_argument("--perf", action="store_true")
    parser.add_argument("--output", required=True)
    parser.set_defaults(nightly=False, perf=False)
    args = parser.parse_args()
    add_test(args.output, args.name,
             cmd=args.cmd, timeout=args.timeout,
             nightly=args.nightly, perf=args.perf)


if __name__ == "__main__":
    main()
