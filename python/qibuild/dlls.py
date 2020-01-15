#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Set of tools to handle DLLs on Windows. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.sh
from qisys import ui


def fix_dlls(sdk_dir, env=None, paths=None, mingw=False):
    """
    Copy the dlls from the toolchains and the other build dirs
    into a sdk directory, so that running the executable just works.
    """
    if not paths:
        return
    dest = os.path.join(sdk_dir, "bin")
    qisys.sh.mkdir(dest, recursive=True)
    dlls_to_copy = list()
    for path in paths:
        bin_dir = os.path.join(path, "bin")
        if not os.path.exists(bin_dir):
            continue
        dlls = os.listdir(bin_dir)
        dlls = [x for x in dlls if x.endswith(".dll")]
        dlls = [os.path.join(bin_dir, x) for x in dlls]
        dlls_to_copy.extend(dlls)
    if mingw:
        # Copy libgcc and mingw dll
        if not env:
            env = os.environ.copy()
        env_path = env["PATH"]
        candidates = env_path.split(os.path.pathsep)
        for candidate in candidates:
            if not os.path.exists(candidate):
                continue
            dlls = os.listdir(candidate)
            dlls = [x for x in dlls if x.endswith(".dll")]
            dlls_to_copy.extend([os.path.join(candidate, x) for x in dlls
                                 if x.startswith("libgcc")])
            dlls_to_copy.extend([os.path.join(candidate, x) for x in dlls
                                 if x.startswith("mingw")])
    for dll_to_copy in dlls_to_copy:
        try:
            qisys.sh.safe_copy(dll_to_copy, dest)
        except Exception as e:
            mess = "Could not copy %s to %s\n" % (dll_to_copy, dest)
            mess += "Error was: %s\n" % e
            ui.warning(mess)
