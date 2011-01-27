#!/usr/bin/env python

r"""This script install qibuild properly on windows.

Only requirement: have c:\pyton26\Scripts in %PATH%
"""
import os
import sys
import stat
import posixpath

CUR_DIR = os.path.abspath(os.path.dirname(__file__))

ON_WIN = sys.platform.startswith("win")

def chmod_755(path):
    """Fix permission of a script"""
    os.chmod(path,
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
        stat.S_IRGRP | stat.S_IXGRP |
        stat.S_IROTH | stat.S_IXOTH)


def install(script_name):
    python_path = os.path.join(CUR_DIR, "python")
    script_path = os.path.join(CUR_DIR, "bin", script_name)
    with open(script_path, "r") as fp:
        script_contents = fp.read()

    script_contents = script_contents.replace("# sys.path", """import sys
sys.path.insert(0, r"%s")""" % python_path)

    # Always install a .py script:
    if ON_WIN:
        dest_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
    else:
        dest_dir = os.path.join("/usr/local/bin")
    out_path = os.path.join(dest_dir, script_name + ".py")
    with open(out_path, "w") as fp:
        fp.write(script_contents)


    chmod_755(out_path)
    print "Script installed in ", out_path

    if not ON_WIN or "--posix" in sys.argv:
        # For convenience, also create a executable without extension
        # in /usr/local/bin:
        if not os.path.exists("/usr/local"):
            os.makedirs("/usr/local")
        out_path = posixpath.join("/usr/local/bin", script_name)
        chmod_755(out_path)
        print "Posix script in ", out_path
        with open(out_path, "w") as fp:
            fp.write(script_contents)


if __name__ == "__main__":
    install("qibuild")
    install("qisrc")



