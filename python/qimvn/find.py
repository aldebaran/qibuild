## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Find a package

"""

import qisys

def find(projects, package):
    """ Search package directly in build directories so,
        this way, we are sure that returned path really point
        on package.
    """
    return qisys.find(projects, package, "target", jar_name)

def jar_name(name):
    """ Append '-*.jar' to name.
        '*' is mandatory because jar name contains binary version.
        (i.e : "foo-1.0-SNAPSHOT.jar")
    """
    return name + "-*.jar"
