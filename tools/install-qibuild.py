## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This script installs qibuild properly

"""
import os
import sys
import stat

CUR_DIR = os.path.abspath(os.path.dirname(__file__))

def chmod_755(path):
    """Fix permission of a script"""
    os.chmod(path,
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
        stat.S_IRGRP | stat.S_IXGRP |
        stat.S_IROTH | stat.S_IXOTH)

def install(script_name):
    python_path = os.path.join(CUR_DIR, "..", "python")
    python_path = os.path.abspath(python_path)
    script_path = os.path.join(python_path, "bin", script_name)
    with open(script_path, "r") as fp:
        script_contents = fp.read()

    script_contents = script_contents.replace("# sys.path", """import sys
sys.path.insert(0, r"%s")""" % python_path)

    if sys.platform.startswith("win"):
        dest_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
    else:
        dest_dir = "/usr/local/bin"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    out_path = os.path.join(dest_dir, script_name + ".py")
    with open(out_path, "w") as fp:
        fp.write(script_contents)
    print "Script installed in ", out_path

    chmod_755(out_path)
    if sys.platform.startswith("win32"):
        # Also create a .bat just in case:
        with open(os.path.join(dest_dir, script_name + ".bat"), "w") as fp:
            fp.write('@echo off\n')
            fp.write('"{python}" "{script}" %*\n'.format(
                python=sys.executable,
                script=out_path))


if __name__ == "__main__":
    install("qitoolchain")
    install("qibuild")
    install("qisrc")
    install("qidoc")



