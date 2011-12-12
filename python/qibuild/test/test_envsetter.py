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

"""Automatic testing for qibuild.EnvSetter

"""


import os
import sys
import unittest
import tempfile

import qibuild


class EnvSetterTestCase(unittest.TestCase):
    def setUp(self):
        # clean up os.environ (simpler debug)
        os.environ = dict()
        # defines useful vars
        if sys.platform.startswith("win"):
            os.environ["PATH"] = r"c:\windows;c:\windows\system32\;"
            self.unlikely = r"c:\program files (x86)\unlikely"
            self.absurd   = r"c:\this\is\absurd"
        else:
            os.environ["PATH"] = "/usr/bin:/usr/local/bin"
            self.unlikely = "/a/very/unlikely/path"
            self.absurd   = "/this/is/absurd"

    def _check_is_in_path(self, directory, path_env):
        """ Check that a given directory is in the given string

        """
        paths = path_env.split(os.path.pathsep)
        mess  = "Could not find %s in %s" % (directory, paths)
        self.assertTrue(directory in paths, mess)

    def test_create_new_env(self):
        # Check that envsetter is able to create new env vars
        envsetter = qibuild.envsetter.EnvSetter()
        envsetter.set_env_var("WITH_SPAM", "ON")
        build_env = envsetter.get_build_env()
        self.assertTrue(build_env.get("WITH_SPAM", "ON"))

    def test_append_to_path(self):
        previous_path = os.environ["PATH"]
        envsetter = qibuild.envsetter.EnvSetter()
        envsetter.append_to_path(self.unlikely)
        build_env = envsetter.get_build_env()
        self.assertEquals(os.environ["PATH"], previous_path)
        new_path = build_env["PATH"]
        self._check_is_in_path(self.unlikely, new_path)

    def test_append_to_path_twice_the_same(self):
        # adding the same path twice should be a no-op
        previous_path = os.environ["PATH"]
        envsetter = qibuild.envsetter.EnvSetter()
        envsetter.append_to_path(self.unlikely)
        path_env1 = envsetter.get_build_env()["PATH"]
        envsetter.append_to_path(self.unlikely)
        path_env2 = envsetter.get_build_env()["PATH"]
        self.assertEquals(os.environ["PATH"], previous_path)
        self.assertEquals(path_env1, path_env2)
        self._check_is_in_path(self.unlikely, path_env1)

    def test_append_to_path_several_times(self):
        # adding two different paths should work
        previous_path = os.environ["PATH"]
        envsetter = qibuild.envsetter.EnvSetter()
        envsetter.append_to_path(self.unlikely)
        envsetter.append_to_path(self.absurd)
        path_env = envsetter.get_build_env()["PATH"]
        self.assertEquals(os.environ["PATH"], previous_path)
        self._check_is_in_path(self.unlikely, path_env)
        self._check_is_in_path(self.absurd  , path_env)

    def test_no_side_effects(self):
        # messing up with the return value of EnvSetter
        # should not change envsetter.get_build_env()
        envsetter = qibuild.envsetter.EnvSetter()
        build_env = envsetter.get_build_env()
        build_env["spam"] = "eggs"
        self.assertTrue(envsetter.get_build_env().get("spam") is None)

    if sys.platform.startswith("win"):
        def test_source_bat(self):
            vc_path  = r'c:\microsoft\vc\bin'
            lib_path = r'c:\microsoft\vc\lib'
            with qibuild.sh.TempDir() as tmp:
                sourceme = os.path.join(tmp, "sourceme.bat")
                to_write = r"""@echo hello world
set PATH=%PATH%;{}
set LIBPATH={}
""".format(vc_path, lib_path)
                with open(sourceme, "w") as fp:
                    fp.write(to_write)
                envsetter = qibuild.envsetter.EnvSetter()
                envsetter.source_bat(sourceme)
                build_env = envsetter.get_build_env()
                # simple assert:
                build_env_path = build_env["PATH"]
                self._check_is_in_path(vc_path, build_env["PATH"])
                self._check_is_in_path(lib_path, build_env["LIBPATH"])
                # sourcing the .bat twice should not change the PATH env var
                envsetter.source_bat(sourceme)
                build_env_path2 = envsetter.get_build_env()["PATH"]
                self.assertEquals(build_env_path2, build_env_path)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
