## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Call package goal on maven project

"""

import os
import qisys.command

def package(project, pom_path=None, skip_test=None):
    """ Find projects directory and call mvn package.
    """
    if not pom_path:
        pom_path = os.path.join(project.path, "pom.xml")
    if not os.path.exists(pom_path):
        raise Exception("No pom.xml in this project (" + pom_path + ")")

    callee = ["mvn"]
    if skip_test:
        callee += ["-Dmaven.test.skip=true"]
    callee += ["-U", "package", "-f", pom_path]
    return qisys.command.call(callee)