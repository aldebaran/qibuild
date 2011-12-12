## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#!/usr/bin/env python

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



