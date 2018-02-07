# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

"""Automatic testing for qibuild.EnvSetter

"""


import os
import sys
import unittest

import qisys.sh
import qisys.envsetter
import qibuild.config


class EnvSetterTestCase(unittest.TestCase):
    def setUp(self):
        self.environ_back = os.environ.copy()
        # clean up os.environ (simpler debug)
        os.environ = dict()
        # defines useful vars
        if sys.platform.startswith("win"):
            os.environ["PATH"] = r"c:\windows;c:\windows\system32\;"
            self.unlikely = r"c:\program files (x86)\unlikely"
            self.absurd = r"c:\this\is\absurd"
        else:
            os.environ["PATH"] = "/usr/bin:/usr/local/bin"
            self.unlikely = "/a/very/unlikely/path"
            self.absurd = "/this/is/absurd"

    def tearDown(self):
        os.environ = self.environ_back.copy()

    def _check_is_in_path(self, directory, path_env):
        """ Check that a given directory is in the given string

        """
        paths = path_env.split(os.path.pathsep)
        mess = "Could not find %s in %s" % (directory, paths)
        self.assertTrue(directory in paths, mess)

    def test_create_new_env(self):
        # Check that envsetter is able to create new env vars
        envsetter = qisys.envsetter.EnvSetter()
        envsetter.set_env_var("WITH_SPAM", "ON")
        build_env = envsetter.get_build_env()
        self.assertTrue(build_env.get("WITH_SPAM", "ON"))

    def test_prepend_to_path(self):
        previous_path = os.environ["PATH"]
        envsetter = qisys.envsetter.EnvSetter()
        envsetter.prepend_to_path(self.unlikely)
        build_env = envsetter.get_build_env()
        self.assertEquals(os.environ["PATH"], previous_path)
        new_path = build_env["PATH"]
        self._check_is_in_path(self.unlikely, new_path)

    def test_prepend_to_path_twice_the_same(self):
        # adding the same path twice should be a no-op
        previous_path = os.environ["PATH"]
        envsetter = qisys.envsetter.EnvSetter()
        envsetter.prepend_to_path(self.unlikely)
        path_env1 = envsetter.get_build_env()["PATH"]
        envsetter.prepend_to_path(self.unlikely)
        path_env2 = envsetter.get_build_env()["PATH"]
        self.assertEquals(os.environ["PATH"], previous_path)
        self.assertEquals(path_env1, path_env2)
        self._check_is_in_path(self.unlikely, path_env1)

    def test_prepend_to_path_multi(self):
        # Adding a directory containing os.path.sep should
        # do the smart thing:
        envsetter = qisys.envsetter.EnvSetter()
        to_add = self.unlikely + os.path.pathsep + self.absurd
        envsetter.prepend_to_path(to_add)
        env_path = envsetter.get_build_env()["PATH"]
        self._check_is_in_path(self.unlikely, env_path)
        self._check_is_in_path(self.absurd, env_path)

    def test_prepend_to_path_several_times(self):
        # adding two different paths should work
        previous_path = os.environ["PATH"]
        envsetter = qisys.envsetter.EnvSetter()
        envsetter.prepend_to_path(self.unlikely)
        envsetter.prepend_to_path(self.absurd)
        path_env = envsetter.get_build_env()["PATH"]
        self.assertEquals(os.environ["PATH"], previous_path)
        self._check_is_in_path(self.unlikely, path_env)
        self._check_is_in_path(self.absurd, path_env)

    def test_no_side_effects(self):
        # messing up with the return value of EnvSetter
        # should not change envsetter.get_build_env()
        envsetter = qisys.envsetter.EnvSetter()
        build_env = envsetter.get_build_env()
        build_env["spam"] = "eggs"
        self.assertTrue(envsetter.get_build_env().get("spam") is None)

    if sys.platform.startswith("win"):
        def test_source_bat(self):
            vc_path = r'c:\microsoft\vc\bin'
            lib_path = r'c:\microsoft\vc\lib'
            with qisys.sh.TempDir() as tmp:
                sourceme = os.path.join(tmp, "sourceme.bat")
                to_write = r"""@echo hello world
set PATH=%PATH%;{}
set LIBPATH={}
""".format(vc_path, lib_path)
                with open(sourceme, "w") as fp:
                    fp.write(to_write)
                envsetter = qisys.envsetter.EnvSetter()
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


def test_reads_env_vars_from_config(tmpdir):
    qibuild_xml = tmpdir.join("qibuild.xml")
    qibuild_xml.write("""
<qibuild>
  <defaults>
    <env>
     <var name="FOO">BAR</var>
    </env>
  </defaults>
  <config name="spam">
    <env>
      <var name="SPAM">EGGS</var>
    </env>
  </config>
</qibuild>
""")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(qibuild_xml.strpath)
    qibuild_cfg.set_active_config("spam")
    env_setter = qisys.envsetter.EnvSetter()
    env_setter.read_config(qibuild_cfg)
    build_env = env_setter.get_build_env()
    assert build_env["FOO"] == "BAR"
    assert build_env["SPAM"] == "EGGS"


def test_updating_env_vars(tmpdir):
    qibuild_xml = tmpdir.join("qibuild.xml")
    qibuild_xml.write("""
<qibuild>
  <defaults>
    <env>
     <var name="FOO">BAR</var>
    </env>
  </defaults>
  <config name="spam">
    <env>
      <var name="FOO">SPAM</var>
    </env>
  </config>
</qibuild>
""")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(qibuild_xml.strpath)
    qibuild_cfg.set_active_config("spam")
    env_setter = qisys.envsetter.EnvSetter()
    env_setter.read_config(qibuild_cfg)
    build_env = env_setter.get_build_env()
    assert build_env["FOO"] == "SPAM"


def test_prepending_variable_already_here():
    env = {
        "PATH": "/foo:/bar"
    }
    envsetter = qisys.envsetter.EnvSetter(build_env=env)
    envsetter.prepend_to_path("/baz")
    envsetter.prepend_to_path("/foo")
    actual = envsetter.get_build_env()["PATH"]
    assert actual == "/foo:/baz:/bar"


def main():
    unittest.main()


if __name__ == "__main__":
    main()
