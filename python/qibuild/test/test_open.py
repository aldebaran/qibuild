## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" testing for qibuild open

"""

import StringIO
import unittest
import mock

import qibuild.actions.open

class FakeToc:
    def __init__(self, active_config=None, local_config=None):
        self.active_config = active_config
        if not local_config:
            self.cfg_path = StringIO.StringIO('<qibuild version="1"/>')
        else:
            self.cfg_path = StringIO.StringIO(local_config)

class OpenTestCase(unittest.TestCase):

    def setUp(self):
        self.cfg_patcher = mock.patch('qibuild.config.get_global_cfg_path')
        self.cfg_mock = self.cfg_patcher.start()
        self.ask_patcher = mock.patch('qibuild.interact.ask_choice')
        self.ask_mock = self.ask_patcher.start()

    def test_no_ide_in_conf(self):
        fake_cfg = StringIO.StringIO('<qibuild version="1" />')
        self.cfg_mock.return_value = fake_cfg
        toc = FakeToc()
        error = None
        try:
            qibuild.actions.open.get_ide(toc)
        except Exception, e:
            error = e
        self.assertFalse(error is None)
        self.assertTrue("Could not find any IDE in configuration" in error.message)
        self.assertFalse(self.ask_mock.called)

    def test_qt_creator_in_conf(self):
        fake_cfg = StringIO.StringIO("""
<qibuild version="1">
  <ide name="QtCreator" path="/path/to/qtsdk/bin/qtcreator" />
</qibuild>
""")
        self.cfg_mock.return_value = fake_cfg
        toc = FakeToc()
        ide = qibuild.actions.open.get_ide(toc)
        self.assertEqual(ide.name, "QtCreator")
        self.assertEqual(ide.path, "/path/to/qtsdk/bin/qtcreator")
        self.assertFalse(self.ask_mock.called)

    def test_eclipse_cdt_in_conf(self):
        fake_cfg = StringIO.StringIO("""
<qibuild version="1">
  <ide name="Eclipse CDT" />
</qibuild>
""")
        self.cfg_mock.return_value = fake_cfg
        toc = FakeToc()
        error = None
        try:
            qibuild.actions.open.get_ide(toc)
        except Exception, e:
            error = e
        self.assertFalse(error is None)
        self.assertFalse("Could not find any IDE in configuration" in error.message)
        self.assertTrue("`qibuild open` only supports" in error.message)

    def test_two_ides(self):
        fake_cfg = StringIO.StringIO(r"""
<qibuild version="1">
  <ide name="Visual Studio" />
  <ide name="QtCreator" path="C:\QtSDK\bin\QtCreator" />
</qibuild>
""")
        self.cfg_mock.return_value = fake_cfg
        self.ask_mock.return_value = "QtCreator"
        toc = FakeToc()
        ide = qibuild.actions.open.get_ide(toc)
        self.assertEqual(ide.name, "QtCreator")
        self.assertEqual(ide.path, r"C:\QtSDK\bin\QtCreator")
        call_args_list = self.ask_mock.call_args_list
        self.assertEqual(len(call_args_list), 1)
        (choices, _question) = call_args_list[0][0]
        self.assertEqual(choices, ['Visual Studio', 'QtCreator'])

    def test_two_ides_matching_default_conf(self):
        fake_cfg = StringIO.StringIO(r"""
<qibuild version="1">
  <config name="win32-vs2010" ide="Visual Studio" />
  <config name="mingw" ide="QtCreator" />
  <ide name="Visual Studio" />
  <ide name="QtCreator" path="C:\QtSDK\bin\QtCreator" />
</qibuild>
""")
        self.cfg_mock.return_value = fake_cfg
        toc = FakeToc(local_config="""
<qibuild version="1">
  <defaults config="mingw" />
</qibuild>
""")

        ide = qibuild.actions.open.get_ide(toc)
        self.assertEqual(ide.name, "QtCreator")
        self.assertEqual(ide.path, r"C:\QtSDK\bin\QtCreator")
        self.assertFalse(self.ask_mock.called)

    def test_two_ides_matching_user_conf(self):
        # A default config in local config file,
        # but user used -c
        fake_cfg = StringIO.StringIO(r"""
<qibuild version="1">
  <config name="win32-vs2010" ide="Visual Studio" />
  <config name="mingw" ide="QtCreator" />
  <ide name="Visual Studio" />
  <ide name="QtCreator" path="C:\QtSDK\bin\QtCreator" />
</qibuild>
""")
        self.cfg_mock.return_value = fake_cfg
        toc = FakeToc(local_config="""
<qibuild version="1">
  <defaults config="mingw" />
</qibuild>
""", active_config="win32-vs2010")
        ide = qibuild.actions.open.get_ide(toc)
        self.assertEqual(ide.name, "Visual Studio")
        self.assertFalse(self.ask_mock.called)


    def tearDown(self):
        self.cfg_patcher.stop()
        self.ask_patcher.stop()

if __name__ == "__main__":
    unittest.main()
