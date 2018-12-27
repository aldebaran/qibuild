#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
This is an equivalent of a C++ program trying to load a
Python module using libqi, but written in Python.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys


def main():
    """ Main Entry Point """
    from_env = os.environ.get("QI_ADDITIONAL_SDK_PREFIXES")
    if not from_env:
        sys.exit("QI_ADDITIONAL_SDK_PREFIXES not set")
    prefixes = from_env.split(os.path.pathsep)
    found = False
    for prefix in prefixes:
        candidate = os.path.join(prefix, "share", "qi", "module", "foo.mod")
        if os.path.exists(candidate):
            found = True
            with open(candidate, "r") as fp:
                contents = fp.read()
                if contents != "python\n":
                    sys.exit("Expected python\\n, got: " + contents)
    if not found:
        sys.exit("foo.mod not found")
    import foo


if __name__ == "__main__":
    main()
