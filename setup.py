## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
from distutils.core import setup

packages = [
    "qisys",
    "qisys.actions",
    "qisrc",
    "qisrc.actions",
    "qibuild",
    "qibuild.actions",
    "qibuild.cmake",
    "qilinguist",
    "qilinguist.actions",
    "qitoolchain",
    "qitoolchain.actions",
    "qitoolchain.binary_package",
    "qimvn",
    "qimvn.actions"
]

scripts = [
    "python/bin/qidoc",
    "python/bin/qilinguist",
    "python/bin/qisrc",
    "python/bin/qibuild",
    "python/bin/qitoolchain",
    "python/bin/qimvn",
]

package_data = {
 "qisrc" : ["templates/project/CMakeLists.txt",
            "templates/project/main.cpp",
            "templates/project/test.cpp",
            "templates/project/qiproject.xml"
           ],
}

def get_qibuild_cmake_files():
    res = list()
    cmake_dest = 'share/cmake'
    for (root, directories, filenames) in os.walk('cmake'):
        rel_root = os.path.relpath(root, 'cmake')
        if rel_root == ".":
            rel_root = ""
        rel_filenames = [os.path.join('cmake', rel_root, x) for x in filenames]
        rel_dest = os.path.join(cmake_dest, rel_root)
        res.append((rel_dest, rel_filenames))
    return res


data_files = get_qibuild_cmake_files()

setup(name="qibuild",
      version="3.1.2",
      description="Compilation of C++ projects made easy!",
      author="Aldebaran Robotics",
      author_email="dmerejkowsky@aldebaran-robotics.com",
      py_modules=['qicd'],
      packages=packages,
      package_dir={'': 'python'},
      package_data=package_data,
      data_files=data_files,
      license="BSD",
      scripts=scripts
)
