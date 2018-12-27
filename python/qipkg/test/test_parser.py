#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qipkg.parsers
import qibuild.config


def test_pml_parser(qipkg_action, args):
    """ Test Pml Parser """
    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("d_pkg")
    meta_pkg_proj = qipkg_action.add_test_project("meta_pkg")
    args.pml_path = os.path.join(meta_pkg_proj.path, "meta_pkg.mpml")
    meta_builder = qipkg.parsers.get_pml_builder(args)
    assert len(meta_builder.pml_builders) == 2
    a_pml = meta_builder.pml_builders[0]
    d_pml = meta_builder.pml_builders[1]
    assert len(a_pml.cmake_builder.projects) == 1
    assert not d_pml.cmake_builder.projects


def test_reads_build_config(qipkg_action, args, toolchains):
    """ Test Reads Build Config """
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("d_pkg")
    meta_pkg_proj = qipkg_action.add_test_project("meta_pkg")
    args.config = "foo"
    args.pml_path = os.path.join(meta_pkg_proj.path, "meta_pkg.mpml")
    meta_builder = qipkg.parsers.get_pml_builder(args)
    a_pml_builder = meta_builder.pml_builders[0]
    build_config = a_pml_builder.build_worktree.build_config
    assert build_config.toolchain.name == "foo"
