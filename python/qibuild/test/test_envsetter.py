## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for qibuild.EnvSetter

"""


import os
import sys
import unittest
import tempfile

import qibuild


class EnvSetterTestCase(unittest.TestCase):
    def setUp(self):
        # clean up path
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

def main():
    unittest.main()

if __name__ == "__main__":
    main()
