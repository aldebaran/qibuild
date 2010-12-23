##
## Author(s):
##    - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

import os
import qibuild.manifest
from   qibuild.toc.buildconfig import BuildConfig

class Project:
    """ store information about a project:
         - source directory
         - build  directory
         - build  configuration
         - dependencies
    """
    def __init__(self, directory, toolchain_name=None):
        self.directory    = directory
        self.name         = os.path.split(directory)[-1]
        self.build_config = BuildConfig()
        qibuild.manifest.verify(os.path.join(directory, "qibuild.manifest"))

    def get_build_dir(self):
        print "Warning please implement Project.get_build_dir"
        build_dir = os.path.join(self.directory, "build")
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        return build_dir

    def get_sdk_dir(self):
        return os.path.join(self.get_build_dir(), "sdk")

    def get_build_flags(self):
        print "Warning please implement Project.get_build_dir"
        return []

