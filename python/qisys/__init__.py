## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Core tools for every qisys.commands

"""

import os
import glob

from qisys import ui

def find(projects, package_name, directory=None, name_func=None):
    """ Abstract find function.
        Return path to found file with decorated name
    """

    for project in projects:
        decorated_name = package_name

        if name_func:
            decorated_name = name_func(package_name)
        if directory:
            target = os.path.join(project.path, directory)

        target = os.path.join(target, decorated_name)
        ui.debug("Looks into " + target)
        for match in glob.glob(target):
            return match
    return None
