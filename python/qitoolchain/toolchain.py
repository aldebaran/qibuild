##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

import os
import qitoolchain

class Toolchain(object):
    def __init__(self, toc, name, feed=None):
        self.toc = toc
        if name == None:
            self.name = "system"
        else:
            self.name = name
        self.feed = feed
        self._projects = list()

    @property
    def projects(self):
        from_conf = self.toc.configstore.get("toolchain", self.name, "provide")
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


