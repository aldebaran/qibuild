#!/usr/bin/env python

r"""This script install qibuild properly on windows.

Only requirement: have c:\pyton26\Scripts in %PATH%
"""
import os
import sys
import stat
import posixpath

CUR_DIR = os.path.abspath(os.path.dirname(__file__))


def install(script_name):
    python_path = os.path.join(CUR_DIR, "python")
    script_path = os.path.join(CUR_DIR, "bin", script_name)
    with open(script_path, "r") as fp:
        script_contents = fp.read()

    script_contents = script_contents.replace("# sys.path", """import sys
sys.path.insert(0, r"%s")""" % python_path)

    dest_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
    out_path = os.path.join(dest_dir, script_name + ".py")
    with open(out_path, "w") as fp:
        fp.write(script_contents)
    print "Script installed in ", out_path

if __name__ == "__main__":
    install("qitoolchain")
    install("qibuild")
    install("qisrc")



