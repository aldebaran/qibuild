## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from distutils.core import setup

packages = [
    "qibuild",
    "qibuild.external",
    "qisrc",
    "qisrc.actions",
    "qibuild",
    "qibuild.actions",
    "qidoc",
    "qidoc.actions",
    "qitoolchain",
    "qitoolchain.actions",
    "qitoolchain.binary_package",
]

scripts = [
    "bin/qidoc",
    "bin/qisrc",
    "bin/qibuild",
    "bin/qitoolchain",
]

package_data = {
 "qibuild" : ["templates/project/CMakeLists.txt",
              "templates/project/main.cpp",
              "templates/project/test.cpp",
              "templates/project/qiproject.xml"
              ]
}

setup(name = 'qibuild',
      version = "1.14.1",
      description = "Compilation of C++ projects made easy!",
      author = "Aldebaran Robotics",
      author_email = "dmerejkowsky@aldebaran-robotics.com",
      packages = packages,
      package_data = package_data,
      license = "BSD",
      scripts = scripts
)
