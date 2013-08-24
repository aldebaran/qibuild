""" Helper script to add a test to <build>/qitests.json """

import argparse
import json
import os


import qitest.conf

def main():
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
    args = parser.parse_args()
    output = args.output
    kwargs = vars(args)
    del kwargs["output"]
    qitest.conf.add_test(output, **kwargs)

if __name__ == "__main__":
    main()
