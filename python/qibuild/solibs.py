#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Set of tools to handle .so on ubuntu 18.04 and higher """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.sh
import qisys.command
from qisys import ui


def fix_solibs(sdk_dir, paths=None):
    """
    Add rpath to relocate the toolchain libraries
    """
    # This directory may not exist, so create it:
    library_path = "./"
    libraries_list = []
    if not os.path.exists(sdk_dir):
        return
    for path in os.listdir(sdk_dir):
        if not os.path.exists(path):
            continue
        lib_dir = os.path.join(sdk_dir, path, "lib")
        if os.path.exists(lib_dir):
            library_path = library_path + ':' + lib_dir
            libs = os.listdir(lib_dir)
            for lib in libs:
                if ".so" in lib and lib not in libraries_list:
                    libraries_list.append(os.path.join(lib_dir, lib))
    for lib in libraries_list:
        patchelf = qisys.command.find_program("patchelf")
        if not patchelf:
            ui.error("Could not find patchelf for fixing so libraries")
        else:
            cmd = [patchelf, "--set-rpath", library_path, lib]
            qisys.command.call(cmd)
