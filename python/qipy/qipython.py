#!/usr/bin/python

import argparse
import os
import sys

import qisys.command
import qibuild.parsers
import qipy.parsers


def main():
    parser = argparse.ArgumentParser()
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("-c", "--config")
    parser.set_defaults(config="system")
    parser.add_argument("py_args", nargs="+")
    args = parser.parse_args()
    config = args.config
    py_args = args.py_args
    python_worktree = qipy.parsers.get_python_worktree(args)
    venv_root = python_worktree.venv_path(args.config)
    if not os.path.exists(venv_root):
        sys.exit("Virtualenv for %s not found" % config)
    if py_args == ["activate"]:
        sourceme = os.path.join(venv_root, "bin", "activate")
        print sourceme
        sys.exit(0)

    python_exe = os.path.join(venv_root, "bin", "python")
    cmd = [python_exe] + py_args
    qisys.command.call(cmd)

if __name__ == "__main__":
    main()
