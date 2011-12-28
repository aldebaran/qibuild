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


""" Automatic testing for qibuild.config.QiBuildConfig

"""

import os
import qibuild
import unittest
from StringIO import StringIO


def cfg_from_string(str, user_config=None):
    cfg_loc = StringIO(str)
    qibuild_cfg = qibuild.config.QiBuildConfig(user_config=user_config)
    qibuild_cfg.read(cfg_loc)
    return qibuild_cfg


def cfg_to_string(cfg):
    cfg_loc = StringIO()
    cfg.write(cfg_loc)
    return cfg_loc.getvalue()

class QiBuildConfig(unittest.TestCase):

    def test_simple(self):
        xml = """
<qibuild>
  <config name="linux32">
    <env path="/path/to/swig" />
  </config>
  <ide name="qtcreator"
      path="/path/to/qtcreator"
  />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertTrue(qibuild_cfg.active_config is None)
        ide = qibuild_cfg.ides["qtcreator"]
        self.assertEquals(ide.name, "qtcreator")
        self.assertEquals(ide.path, "/path/to/qtcreator")

        config = qibuild_cfg.configs["linux32"]
        self.assertEquals(config.name, "linux32")
        env_path = config.env.path
        self.assertEquals(env_path, "/path/to/swig")

    def test_several_configs(self):
        xml = """
<qibuild>
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
  <config name="linux64">
    <env path="/path/to/swig64" />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        configs = qibuild_cfg.configs
        self.assertEquals(len(configs), 2)
        [linux32_cfg, linux64_cfg] = [configs["linux32"], configs["linux64"]]


        self.assertEquals(linux32_cfg.name, "linux32")
        self.assertEquals(linux64_cfg.name, "linux64")

        self.assertEquals(linux32_cfg.env.path, "/path/to/swig32")
        self.assertEquals(linux64_cfg.env.path, "/path/to/swig64")

    def test_default_from_conf(self):
        xml = """
<qibuild>
  <defaults config="linux32" />
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
  <config name="linux64">
    <env path="/path/to/swig64" />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.defaults.config, "linux32")
        self.assertEquals(qibuild_cfg.active_config, "linux32")
        self.assertEquals(qibuild_cfg.env.path, "/path/to/swig32")

    def test_user_active_conf(self):
        xml = """
<qibuild>
  <defaults config="linux32" />
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
  <config name="linux64">
    <env path="/path/to/swig64" />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml, user_config="linux64")
        self.assertEquals(qibuild_cfg.defaults.config, "linux32")
        self.assertEquals(qibuild_cfg.active_config, "linux64")
        self.assertEquals(qibuild_cfg.env.path, "/path/to/swig64")

    def test_path_merging(self):
        xml = """
<qibuild>
  <defaults>
    <env path="/path/to/foo" />
  </defaults>
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml, user_config="linux32")
        excpected_path = qibuild.sh.to_native_path("/path/to/swig32")
        excpected_path += os.path.pathsep
        excpected_path += qibuild.sh.to_native_path("/path/to/foo")
        self.assertEquals(qibuild_cfg.env.path, excpected_path)

    def test_ide_selection(self):
        xml = """
<qibuild>
  <defaults ide="qtcreator" />
  <ide name="qtcreator"
    path="/path/to/qtcreator"
  />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.ide.path, "/path/to/qtcreator")

    def test_add_env_config(self):
        xml = """
<qibuild>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        config = qibuild.config.Config()
        config.name = "linux32"
        config.env.path = "/path/to/swig32"
        qibuild_cfg.add_config(config)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEquals(len(new_cfg.configs), 1)
        linux32_conf = new_cfg.configs["linux32"]
        self.assertEquals(linux32_conf.env.path, "/path/to/swig32")

    def test_add_cmake_config(self):
        qibuild_cfg = cfg_from_string("<qibuild />")
        config = qibuild.config.Config()
        config.name = "mac64"
        config.cmake.generator = "Xcode"
        qibuild_cfg.add_config(config)
        qibuild_cfg.set_default_config("mac64")
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEquals(new_cfg.cmake.generator, "Xcode")

    def test_default_cmake_generator(self):
        xml = """
<qibuild>
  <defaults>
    <cmake generator="Visual Studio 10" />
  </defaults>
  <config name="win32-mingw">
    <cmake generator="NMake Makefiles" />
  </config>
</qibuild>
"""
        default_cfg = cfg_from_string(xml)
        self.assertEquals(default_cfg.cmake.generator, "Visual Studio 10")
        mingw_cfg  = cfg_from_string(xml, user_config="win32-mingw")
        self.assertEquals(mingw_cfg.cmake.generator, "NMake Makefiles")


    def test_set_default_config(self):
        xml = """
<qibuild>
  <config name="linux32">
    <cmake
        generator="Unix Makefiles"
    />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.cmake.generator, None)
        qibuild_cfg.set_default_config("linux32")
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEquals(new_cfg.cmake.generator, "Unix Makefiles")

    def test_change_default_config(self):
        xml = """
<qibuild>
  <defaults config="linux32" />
  <config name="linux32">
    <cmake
        generator="Unix Makefiles"
    />
  </config>
  <config name="win32-vs2010">
    <cmake
        generator="Visual Studio 10"
    />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.cmake.generator, "Unix Makefiles")
        qibuild_cfg.set_default_config("win32-vs2010")
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEquals(new_cfg.cmake.generator, "Visual Studio 10")

    def test_add_ide(self):
        xml = """
<qibuild>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.ide, None)
        ide = qibuild.config.IDE()
        ide.name = "qtcreator"
        qibuild_cfg.add_ide(ide)
        qibuild_cfg.set_default_ide("qtcreator")
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEquals(new_cfg.ide.name, "qtcreator")

    def test_adding_conf_twice(self):
        xml = """
<qibuild>
  <config name="linux32" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        config = qibuild.config.Config()
        config.name = "linux32"
        config.cmake.generator = "Code::Blocks"
        qibuild_cfg.add_config(config)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEqual(new_cfg.configs["linux32"].cmake.generator,
            "Code::Blocks")


    def test_ide_from_config(self):
        xml = """
<qibuild>
  <ide
    name = "Visual Studio"
  />
  <ide
    name = "QtCreator"
    path  = "/path/to/qtsdk/qtcreator"
  />
  <config
    name = "win32-vs2010"
    ide  = "Visual Studio"
  />
  <config
    name = "win32-mingw"
    ide  = "QtCreator"
  />
</qibuild>
"""
        qt_cfg = cfg_from_string(xml, "win32-vs2010")
        self.assertEqual(qt_cfg.ide.name, "Visual Studio")
        self.assertTrue(qt_cfg.ide.path is None)
        vc_cfg = cfg_from_string(xml, "win32-mingw")
        self.assertEqual(vc_cfg.ide.name, "QtCreator")
        self.assertEqual(vc_cfg.ide.path, "/path/to/qtsdk/qtcreator")


    def test_adding_ide_twice(self):
        xml = """
<qibuild>
  <ide name="qtcreator" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        ide = qibuild.config.IDE()
        ide.name = "qtcreator"
        ide.path = "/path/to/qtcreator"
        qibuild_cfg.add_ide(ide)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEqual(new_cfg.ides["qtcreator"].path,
            "/path/to/qtcreator")


    def test_build_settings(self):
        xml = """
<qibuild>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertFalse(qibuild_cfg.build.incredibuild)
        self.assertTrue(qibuild_cfg.build.sdk_dir   is None)
        self.assertTrue(qibuild_cfg.build.build_dir is None)

        xml = """
<qibuild>
    <build
        sdk_dir="/path/to/sdk"
        build_dir="/path/to/build"
        incredibuild="Yes"
    />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertTrue(qibuild_cfg.build.incredibuild)
        self.assertEqual(qibuild_cfg.build.sdk_dir,
            qibuild.sh.to_native_path("/path/to/sdk"))
        self.assertEqual(qibuild_cfg.build.build_dir,
            qibuild.sh.to_native_path("/path/to/build"))

    def test_set_manifest_url(self):
        xml = """
<qibuild>
</qibuild>
"""
        manifest_url = "http://example.com/qi/foo.xml"
        qibuild_cfg = cfg_from_string(xml)
        self.assertTrue(qibuild_cfg.manifest is None)
        qibuild_cfg.set_manifest_url(manifest_url)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertFalse(new_cfg.manifest is None)
        self.assertEqual(new_cfg.manifest.url, manifest_url)



if __name__ == "__main__":
    unittest.main()




