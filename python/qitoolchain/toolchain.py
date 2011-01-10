##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

import os
import qitoolchain
from qitools.configstore import ConfigStore


def get_config_path():
    """Returns a suitable config path"""
    # FIXME: deal with non-UNIX systems
    config_path = os.path.expanduser("~/.config/qi/toolchain.cfg")
    return config_path

class Toolchain(object):
    def __init__(self, name):
        if name == None:
            self.name = "system"
        else:
            self.name = name
        self.feed = None
        self.config_path = get_config_path()
        self.configstore = ConfigStore()
        self.configstore.read(get_config_path())
        self.feed = self.configstore.get("toolchain", self.name, "feed")
        self._projects = list()

    @property
    def projects(self):
        from_conf = self.configstore.get("toolchain", self.name, "provide")
        if from_conf:
            self._projects = from_conf.split()
        else:
            self._projects = list()
        return self._projects

    def get(self, package_name):
        """Return path to a package """
        base_dir = qitoolchain.get_rootfs(self.name)
        package_path = os.path.join(base_dir, package_name)
        return package_path


