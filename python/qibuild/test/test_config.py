## Copyright (C) 2011 Aldebaran Robotics

"""Automatic testing for handling qibuidl configurations

"""
import os
import unittest

import qibuild



class QiConfigTestCase(unittest.TestCase):
    def setUp(self):
        """ An (almost) realistic exemple ...

        """

        name_to_config = {
        "general" : """
[env]
path = /opt/local/swig/bin

""",
        "local" : """
[project foo]
cmake.flags = SPAM=EGGS

# Default build configuration:
[build]
config = mac64
""",
        "mac32" : """
[build]
cmake.flags = CMAKE_OSX_ARCHITECTURES=i386
cmake.generator = 'Unix Makefiles'

""",
        "mac64" : """
[build]
cmake.generator = 'XCode'

"""
        }

        self.config = qibuild.configstore.MultiConfigstore()

        # Create files with the correct contents at random places:
        with qibuild.sh.TempDir() as tmp:
            for (name, config) in name_to_config.iteritems():
                filename = os.path.join(tmp, name)
                fp = open(filename, "w")
                fp.write(config)
                fp.close()
                self.config.add_file(name, filename)

    def test_default_config(self):
        self.assertEquals(self.config.get('build', 'config'),
            'mac64')
        self.assertEquals(self.config.get('env', 'path'),
            '/opt/local/swig/bin')
        self.assertEquals(self.config.get('build', 'cmake', 'generator'),
            'XCode')
        self.assertTrue(self.config.get('build', 'cmake', 'flags') is None)
        self.assertEquals(self.config.get('project', 'foo', 'cmake', 'flags'),
            'SPAM=EGGS')

    def test_setting_config(self):
        self.config.set_user_config('mac32')

        self.assertEquals(self.config.get_current_config(), 'mac32')
        self.assertEquals(self.config.get('env', 'path'),
            '/opt/local/swig/bin')
        self.assertEquals(self.config.get('build', 'cmake', 'generator'),
            'Unix Makefiles')
        self.assertEquals(self.config.get('build', 'cmake', 'flags'),
            'CMAKE_OSX_ARCHITECTURES=i386')
        self.assertEquals(self.config.get('project', 'foo', 'cmake', 'flags'),
            'SPAM=EGGS')


if __name__ == "__main__":
    unittest.main()
