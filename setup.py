## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
from setuptools import setup, find_packages

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
      version="3.8.2",
      description="The meta build framework",
      url="https://community.aldebaran-robotics.com/doc/qibuild/",
      author="Aldebaran Robotics",
      author_email="qibuild-dev@aldebaran-robotics.com",
      py_modules=['qicd'],
      packages=find_packages("python"),
      package_dir={"": "python"},
      include_package_data = True,
      data_files=data_files,
      license="BSD",
      entry_points = {
        "console_scripts" : [
            "qidoc        = qisys.main:main",
            "qilinguist   = qisys.main:main",
            "qisrc        = qisys.main:main",
            "qibuild      = qisys.main:main",
            "qipkg        = qisys.main:main",
            "qipy         = qisys.main:main",
            "qitest       = qisys.main:main",
            "qitoolchain  = qisys.main:main",
            "qimvn        = qisys.main:main",
        ]
    }
)
