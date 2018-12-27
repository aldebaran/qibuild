#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Test Config.
Automatic testing for qibuild.config.QiBuildConfig.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import io
import unittest

import qibuild
import qibuild.config


def cfg_from_string(input_str, user_config=None):
    """ Config From String """
    cfg_loc = io.BytesIO(input_str.encode("utf-8"))
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(cfg_loc)
    if user_config:
        qibuild_cfg.set_active_config(user_config)
    return qibuild_cfg


def cfg_to_string(cfg):
    """ Config To String """
    cfg_loc = io.BytesIO()
    cfg.write(cfg_loc)
    return cfg_loc.getvalue()


def local_cfg_to_string(cfg):
    """ Local Config To String """
    cfg_loc = io.BytesIO()
    cfg.write_local_config(cfg_loc)
    return cfg_loc.getvalue()


class QiBuildConfig(unittest.TestCase):
    """ QiBuildConfig Test Case """

    def test_simple(self):
        """ Test Simple """
        xml = """
<qibuild version="1">
  <config name="linux32">
    <env path="/path/to/swig" />
  </config>
  <ide name="qtcreator"
      path="/path/to/qtcreator"
  />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        ide = qibuild_cfg.ides["qtcreator"]
        self.assertEquals(ide.name, "qtcreator")
        self.assertEquals(ide.path, "/path/to/qtcreator")
        config = qibuild_cfg.configs["linux32"]
        self.assertEquals(config.name, "linux32")
        env_path = config.env.path
        self.assertEquals(env_path, "/path/to/swig")

    def test_several_configs(self):
        """ Test Several Configs """
        xml = """
<qibuild version="1">
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
        """ Test Default From Conf """
        xml = """
<qibuild version="1">
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
  <config name="linux64">
    <env path="/path/to/swig64" />
  </config>
</qibuild>
"""
        local_xml = """
<qibuild version="1">
  <defaults config="linux32" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        qibuild_cfg.read_local_config(io.BytesIO(local_xml.encode("utf-8")))
        self.assertEquals(qibuild_cfg.local.defaults.config, "linux32")
        self.assertEquals(qibuild_cfg.env.path, "/path/to/swig32")

    def test_user_active_conf(self):
        """ Test User Active Conf """
        xml = """
<qibuild version="1">
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
  <config name="linux64">
    <env path="/path/to/swig64" />
  </config>
</qibuild>
"""
        local_xml = """
<qibuild version="1">
  <defaults config="linux32" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml, user_config="linux64")
        qibuild_cfg.read_local_config(io.BytesIO(local_xml.encode("utf-8")))
        self.assertEquals(qibuild_cfg.local.defaults.config, "linux32")
        self.assertEquals(qibuild_cfg.env.path, "/path/to/swig32")

    def test_path_merging(self):
        """ Test Path Merging """
        xml = """
<qibuild version="1">
  <defaults>
    <env path="/path/to/foo" />
  </defaults>
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml, user_config="linux32")
        excpected_path = "/path/to/swig32"
        excpected_path += os.path.pathsep
        excpected_path += "/path/to/foo"
        self.assertEquals(qibuild_cfg.env.path, excpected_path)

    def test_ide_selection(self):
        """ Test IDE Selection """
        xml = """
<qibuild version="1">
  <defaults ide="qtcreator" />
  <ide name="qtcreator"
    path="/path/to/qtcreator"
  />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.ide.path, "/path/to/qtcreator")

    def test_add_env_config(self):
        """ Test Add Env Config """
        xml = """
<qibuild version="1" />
"""
        qibuild_cfg = cfg_from_string(xml)
        config = qibuild.config.BuildConfig()
        config.name = "linux32"
        config.env.path = "/path/to/swig32"
        qibuild_cfg.add_config(config)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEquals(len(new_cfg.configs), 1)
        linux32_conf = new_cfg.configs["linux32"]
        self.assertEquals(linux32_conf.env.path, "/path/to/swig32")

    def test_add_cmake_config(self):
        """ Test Add CMake Config """
        qibuild_cfg = cfg_from_string("<qibuild />")
        config = qibuild.config.BuildConfig()
        config.name = "mac64"
        config.cmake.generator = "Xcode"
        qibuild_cfg.add_config(config)
        qibuild_cfg.set_default_config("mac64")
        local_xml = local_cfg_to_string(qibuild_cfg)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        new_cfg.read_local_config(io.BytesIO(local_xml))
        self.assertEquals(new_cfg.cmake.generator, "Xcode")

    def test_default_cmake_generator(self):
        """ Test Default CMake Generator """
        xml = """
<qibuild version="1">
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
        mingw_cfg = cfg_from_string(xml, user_config="win32-mingw")
        self.assertEquals(mingw_cfg.cmake.generator, "NMake Makefiles")

    def test_set_default_config(self):
        """ Test Set Default Config """
        xml = """
<qibuild version="1">
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
        local_xml = local_cfg_to_string(qibuild_cfg)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        new_cfg.read_local_config(io.BytesIO(local_xml))
        self.assertEquals(new_cfg.cmake.generator, "Unix Makefiles")

    def test_change_default_config(self):
        """ Test Change Default Config """
        xml = """
<qibuild version="1">
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
        local_xml = """
<qibuild version="1">
  <defaults config="linux32" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        qibuild_cfg.read_local_config(io.BytesIO(local_xml.encode("utf-8")))
        self.assertEquals(qibuild_cfg.cmake.generator, "Unix Makefiles")
        qibuild_cfg.set_default_config("win32-vs2010")
        local_xml = local_cfg_to_string(qibuild_cfg)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        new_cfg.read_local_config(io.BytesIO(local_xml))
        self.assertEquals(new_cfg.cmake.generator, "Visual Studio 10")

    def test_add_ide(self):
        """ Test Add Ide """
        xml = """\n<qibuild version="1">\n</qibuild>\n"""
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
        """ Test Adding Conf Twice """
        xml = """\n<qibuild version="1">\n  <config name="linux32" />\n</qibuild>\n"""
        qibuild_cfg = cfg_from_string(xml)
        config = qibuild.config.BuildConfig()
        config.name = "linux32"
        config.cmake.generator = "Code::Blocks"
        qibuild_cfg.add_config(config)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEqual(new_cfg.configs["linux32"].cmake.generator,
                         "Code::Blocks")

    def test_ide_from_config(self):
        """ Test IDE From Config """
        xml = """
<qibuild version="1">
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
        """ Test Adding IDE Twice """
        xml = """
<qibuild version="1">
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
        """ Test Build Settings """
        xml = """
<qibuild version="1">
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertTrue(qibuild_cfg.local.build.sdk_dir is None)
        self.assertTrue(qibuild_cfg.local.build.prefix is None)
        xml = """
<qibuild version="1">
</qibuild>
"""
        local_xml = """
<qibuild version="1">
  <build
    sdk_dir="/path/to/sdk"
    prefix="/path/to/build"
  />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        qibuild_cfg.read_local_config(io.BytesIO(local_xml.encode("utf-8")))
        self.assertEqual(qibuild_cfg.local.build.sdk_dir, "/path/to/sdk")
        self.assertEqual(qibuild_cfg.local.build.prefix, "/path/to/build")

    def test_get_server_access(self):
        """ Test Get Server Access """
        xml = """
<qibuild version="1">
  <server name="example.com">
    <access
      username="john"
      password="p4ssw0rd"
      root="root"
    />
  </server>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        # Just make sure setting is kept:
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        server_name = "example.com"
        access = new_cfg.get_server_access(server_name)
        self.assertEqual(access.username, "john")
        self.assertEqual(access.password, "p4ssw0rd")
        self.assertEqual(access.root, "root")
        access = new_cfg.get_server_access("doesnotexists")
        self.assertTrue(access is None)

    def test_set_server_access(self):
        """ Test Set Server Access """
        xml = '<qibuild />'
        qibuild_cfg = cfg_from_string(xml)
        qibuild_cfg.set_server_access("gerrit", "john")
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        access = new_cfg.get_server_access("gerrit")
        self.assertEqual(access.username, "john")

    def test_change_server_access(self):
        """ Test Change Server Access """
        xml = """
<qibuild version="1">
    <server name="gerrit">
        <access username="steve" />
    </server>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        qibuild_cfg.set_server_access("gerrit", "john")
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        access = new_cfg.get_server_access("gerrit")
        self.assertEqual(access.username, "john")

    def test_merge_settings_with_empty_active(self):
        """ Test Merge Settings With Empty Active """
        xml = """
<qibuild version="1">
  <defaults>
      <cmake generator="NMake Makefiles" />
  </defaults>

  <config name="win32-vs2010" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.cmake.generator, "NMake Makefiles")
        qibuild_cfg.set_active_config("win32-vs2010")
        self.assertEquals(qibuild_cfg.cmake.generator, "NMake Makefiles")

    def test_build_farm_config(self):
        """ Test BuildFarm Config """
        xml = r"""
<qibuild version="1">
  <build/>
  <defaults>
    <env path="C:\Program Files\swigwin-2.0.1;C:\Program Files (x86)\dotNetInstaller\bin;C:\Program Files (x86)\Windows Installer XML v3.5\bin" bat_file="C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat"/>
    <cmake generator="NMake Makefiles"/>
  </defaults>
  <config name="win32-vs2010">
    <env/>
    <cmake/>
  </config>
</qibuild>
"""  # noqa
        qibuild_cfg = cfg_from_string(xml, user_config='win32-vs2010')
        self.assertEquals(qibuild_cfg.cmake.generator, "NMake Makefiles")


def test_recompute_cmake_generator(tmpdir):
    """ Test ReCompute CMake Generator """
    global_xml = tmpdir.join("global.xml")
    global_xml.write("""
<qibuild>
  <config name="a">
    <cmake generator="A" />
  </config>
  <config name="b" />
</qibuild>
""")
    local_xml = tmpdir.join("local.xml")
    local_xml.write("""
<qibuild>
  <defaults config="a" />
</qibuild>
""")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath)
    qibuild_cfg.read_local_config(local_xml.strpath)
    assert qibuild_cfg.cmake.generator == "A"
    qibuild_cfg.set_active_config("b")
    assert qibuild_cfg.cmake.generator is None


def test_worktree_paths(tmpdir):
    """ Test WorkTree Paths """
    global_xml = tmpdir.join("global.xml")
    global_xml.write("""
<qibuild>
    <worktree path="/path/to/a" />
    <worktree path="/path/to/b" />
</qibuild>
""")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath)
    assert "/path/to/a" in qibuild_cfg.worktrees
    assert "/path/to/b" in qibuild_cfg.worktrees


def test_do_not_leak_default_config(tmpdir):
    """ Test Do Not Leak Default Config """
    global_xml = tmpdir.join("global.xml")
    global_xml.write("""
<qibuild>
  <config name="system-qt">
    <env path="/opt/qt/bin" bat_file="/path/to/foo.bat" ide="qtcreator"/>
  </config>
  <config name="no-qt" />
</qibuild>
""")
    local_xml = tmpdir.join("local.xml")
    local_xml.write("""
<qibuild>
  <defaults config="system-qt" />
</qibuild>
""")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath)
    qibuild_cfg.read_local_config(local_xml.strpath)
    qibuild_cfg.set_active_config("no-qt")
    assert qibuild_cfg.env.path is None
    assert qibuild_cfg.env.bat_file is None
    assert qibuild_cfg.ide is None


def test_read_default_config_for_worktree(tmpdir):
    """ Test Relad Default Config For Worktree """
    global_xml = tmpdir.join("global.xml")
    global_xml.write("""
<qibuild>
  <worktree path="/path/to/a">
    <defaults config="foo" />
  </worktree>
</qibuild>
""")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath)
    assert qibuild_cfg.get_default_config_for_worktree("/path/to/a") == "foo"


def test_set_default_config_for_worktree(tmpdir):
    """ Test Set Default Config For Worktree """
    global_xml = tmpdir.join("global.xml")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath, create_if_missing=True)
    qibuild_cfg.set_default_config_for_worktree("/path/to/a", "foo")
    qibuild_cfg.write(xml_path=global_xml.strpath)
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath)
    assert qibuild_cfg.get_default_config_for_worktree("/path/to/a") == "foo"


def test_parse_build_configs(tmpdir):
    """ Test Parse Build Configs """
    global_xml = tmpdir.join("global.xml")
    global_xml.write("""
<qibuild>
  <config name="nao-arm">
    <toolchain>arm</toolchain>
    <profiles>
      <profile>nao</profile>
      <profile>arm</profile>
    </profiles>
  </config>
</qibuild>
""")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath)
    nao_arm = qibuild_cfg.configs["nao-arm"]
    assert nao_arm.toolchain == "arm"
    assert nao_arm.profiles == ["nao", "arm"]


def test_write_build_configs(tmpdir):
    """ Test Write Buid Configs """
    global_xml = tmpdir.join("global.xml")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath, create_if_missing=True)
    foo_config = qibuild.config.BuildConfig()
    foo_config.name = "foo"
    foo_config.toolchain = "bar"
    foo_config.profiles = ["spam", "eggs"]
    qibuild_cfg.add_config(foo_config)
    qibuild_cfg.write(global_xml.strpath)
    qibuild_cfg2 = qibuild.config.QiBuildConfig()
    qibuild_cfg2.read(global_xml.strpath)
    foo_config2 = qibuild_cfg2.configs.get("foo")
    assert foo_config2.name == "foo"
    assert foo_config2.toolchain == "bar"
    assert foo_config2.profiles == ["spam", "eggs"]


def test_host_config_default_is_none(tmpdir):
    """ Test Host Config Default Is None """
    global_xml = tmpdir.join("global.xml")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(global_xml.strpath, create_if_missing=True)
    assert qibuild_cfg.get_host_config() is None


def test_host_config_setting_host():
    """ Test Host Config Setting Host """
    qibuild.config.add_build_config("foo")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    qibuild_cfg.set_host_config("foo")
    assert qibuild_cfg.get_host_config() == "foo"


def test_host_config_is_persistent():
    """ Test Host Config Is Persistent """
    qibuild.config.add_build_config("foo")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    qibuild_cfg.set_host_config("foo")
    qibuild_cfg.write()
    qibuild_cfg2 = qibuild.config.QiBuildConfig()
    qibuild_cfg2.read()
    assert qibuild_cfg2.get_host_config() == "foo"


def test_host_config_is_unique():
    """ Test Host Config Is Unique """
    qibuild.config.add_build_config("foo")
    qibuild.config.add_build_config("bar")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    qibuild_cfg.set_host_config("foo")
    assert qibuild_cfg.configs["foo"].host
    qibuild_cfg.set_host_config("bar")
    assert not qibuild_cfg.configs["foo"].host
    assert qibuild_cfg.configs["bar"].host


def test_setting_env_vars(tmpdir):
    """ Test Setting Env Var """
    global_xml = tmpdir.join("global.xml")
    global_xml.write("""
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
    qibuild_cfg.read(global_xml.strpath)
    qibuild_cfg.set_active_config("spam")
    assert qibuild_cfg.env.vars == {"SPAM": "EGGS", "FOO": "BAR"}
