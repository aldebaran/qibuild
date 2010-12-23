##
## Author(s):
##    - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

import os
import qibuild.manifest

class Project:
    """ store information about a project:
         - source directory
         - build  directory
         - build  configuration
         - dependencies
    """
    def __init__(self, directory):
        self.directory = directory
        self.name      = os.path.split(directory)[-1]
        qibuild.manifest.verify(os.path.join(directory, "qibuild.manifest"))
