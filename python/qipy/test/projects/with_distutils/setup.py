## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from setuptools import setup

setup(name="with_distutils",
      py_modules=["foo"],
      entry_points = {"console_scripts" : ["foo = foo:main"]}
)
