## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from distutils.core import setup

packages = [
    "qibuild",
    "qisys",
    "qisrc",
    "qisrc.actions",
    "qibuild",
    "qibuild.actions",
    "qibuild.cmake",
    "qidoc",
    "qidoc.actions",
    "qidoc.docs",
    "qilinguist",
    "qilinguist.actions",
    "qitoolchain",
    "qitoolchain.actions",
    "qitoolchain.binary_package",
]

scripts = [
    "bin/qidoc",
    "bin/qilinguist",
    "bin/qisrc",
    "bin/qibuild",
    "bin/qitoolchain",
]

package_data = {
 "qisrc" : ["templates/project/CMakeLists.txt",
            "templates/project/main.cpp",
            "templates/project/test.cpp",
            "templates/project/qiproject.xml"
           ]
}

setup(name = 'qibuild',
      version = "2.4",
      description = "Compilation of C++ projects made easy!",
      author = "Aldebaran Robotics",
      author_email = "dmerejkowsky@aldebaran-robotics.com",
      packages = packages,
      package_data = package_data,
      license = "BSD",
      scripts = scripts
)
