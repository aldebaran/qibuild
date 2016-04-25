from __future__ import print_function

import argparse
import shutil
import sys

print("sys.argv:", "\n".join(sys.argv))
parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")
parser.add_argument("--fail", action="store_true")
parser.set_defaults(fail=False)
args = parser.parse_args()

print(args.input, "->", args.output)
shutil.copy(args.input, args.output)

if args.fail:
    sys.exit("gen.py failed")
