
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
from setuptools import setup, find_packages

setup(name="hello",
      version="0.1",
      description="a test",
      url="https://example.com",
      py_modules=['hello'],
      entry_points = {
        "console_scripts" : [
            "hello = hello:main",
         ]
        }
)
