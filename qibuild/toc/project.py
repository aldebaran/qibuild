##
## Author(s):
##    - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

import os
from   qibuild.toc.buildconfig import BuildConfig

class Project:
    """ store information about a project:
         - source directory
         - build  directory
         - build  configuration
         - dependencies
    """
    def __init__(self, directory):
        self.directory    = directory
        self.name         = os.path.split(directory)[-1]
        self.build_config = BuildConfig()

    def get_sdk_dir(self):
        return os.path.join(self.build_config.build_directory, "sdk")
