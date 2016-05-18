## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import sys
from setuptools import setup, find_packages

if (sys.version_info.major, sys.version_info.minor) != (2, 7):
    sys.exit("Error: qibuild only works with Python2.7")

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
      version="3.11.6",
      description="The meta build framework",
      url="http://doc.aldebaran.com/qibuild",
      author="Aldebaran Robotics",
      author_email="qibuild-dev@aldebaran-robotics.com",
      py_modules=['qicd'],
      packages=find_packages("python"),
      package_dir={"": "python"},
      include_package_data = True,
      install_requires=["virtualenv"],
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
        ]
    }
)
