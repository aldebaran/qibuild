#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild Setup """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
from setuptools import setup, find_packages


def get_qibuild_cmake_files():
    """ Get QiBuild CMake Files """
    res = list()
    cmake_dest = 'share/cmake'
    for (root, _dirs, filenames) in os.walk('cmake'):
        rel_root = os.path.relpath(root, 'cmake')
        if rel_root == ".":
            rel_root = ""
        rel_filenames = [os.path.join('cmake', rel_root, x) for x in filenames]
        rel_dest = os.path.join(cmake_dest, rel_root)
        res.append((rel_dest, rel_filenames))
    return res


setup(
    name="qibuild",
    version="3.14.1",
    license="BSD",
    description="The Meta Build Framework",
    url="http://doc.aldebaran.com/qibuild",
    author="SoftBank Robotics",
    author_email="qibuild-dev@aldebaran-robotics.com",
    py_modules=["qicd"],
    packages=find_packages("python"),
    package_dir={"": str("python")},
    data_files=get_qibuild_cmake_files(),
    include_package_data=True,
    install_requires=[
        "six>=1.11",
        "sphinx<=1.3.1",
        "sphinx_intl<=0.9.5",
        "tabulate>=0.8",
        "virtualenv>=16",
        "python-minifier>=2.1",
    ],
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Version Control :: Git'
          ],
    entry_points={
        "console_scripts": [
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
