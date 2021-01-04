#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import platform

import qisys.command
import qipkg.metabuilder

TARGET = "{}-{}".format(platform.system().lower(),
                        platform.processor().lower())


def test_meta_builder(qipkg_action):
    """ Test Meta Builder """
    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("d_pkg")
    meta_pkg_proj = qipkg_action.add_test_project("meta_pkg")
    meta_pml = os.path.join(meta_pkg_proj.path, "meta_pkg.mpml")
    worktree = qipkg_action.worktree
    meta_pml_builder = qipkg.metabuilder.MetaPMLBuilder(meta_pml, worktree=worktree)
    meta_pml_builder.configure()
    meta_pml_builder.build()
    dump_syms = qisys.command.find_program("dump_syms")
    if dump_syms:
        with_breakpad = True
    else:
        with_breakpad = False
    packages = meta_pml_builder.package(with_breakpad=with_breakpad)
    contents = [os.path.basename(x) for x in packages]
    if with_breakpad:
        assert contents == ['a-0.1-{}.pkg'.format(TARGET),
                            'a-0.1-symbols-{}.zip'.format(TARGET),
                            'd-0.1-{}.pkg'.format(TARGET)]
    else:
        assert contents == ['a-0.1-{}.pkg'.format(TARGET),
                            'd-0.1-{}.pkg'.format(TARGET)]
