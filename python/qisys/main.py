#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Entry point for most of qibuild scripts """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import argparse

import qibuild
import qibuild.cmake
import qisys.script


def print_version(script_name):
    """ Print QiBuild Version """
    # TODO: Version number should be at one place only
    sys.stdout.write("%s version 3.13\n" % script_name)
    qibuild_dir = os.path.dirname(qibuild.__file__)
    python_dir = os.path.dirname(qibuild_dir)
    print("Using Python code from", python_dir)
    if script_name == "qibuild":
        print("Using CMake code from", qibuild.cmake.get_cmake_qibuild_dir())


def main():
    """ Main Entry Point """
    script_name = sys.argv[0]
    # setuptools on windows creates a foo-script.py
    if os.name == 'nt':
        script_name = script_name.replace("-script", "")
        script_name = script_name.replace(".py", "")
    script_name = os.path.basename(script_name)
    parser = argparse.ArgumentParser()
    package_name = ("%s.actions" % script_name)
    modules = qisys.script.action_modules_from_package(package_name)
    if len(sys.argv) == 2 and sys.argv[1] == '--version':
        print_version(script_name)
        sys.exit(0)
    qisys.script.root_command_main(script_name, parser, modules)


if __name__ == "__main__":
    sys.argv.pop(0)
    main()
