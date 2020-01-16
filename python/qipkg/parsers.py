#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Generate a binary package, ready to be used for a behavior """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qipkg.builder
import qipkg.metabuilder
import qipkg.metapackage
import qibuild.parsers


def pml_parser(parser):
    """ Pml Parser """
    qisys.parsers.build_parser(parser)
    parser.add_argument("pml_path")


def pkg_parser(parser):
    """ Pkg Parser """
    parser.add_argument("--with-breakpad", action="store_true")
    parser.add_argument("--with-toolchain", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--python-minify", action="store_true")
    parser.set_defaults(with_breakpad=False, force=False,
                        with_toolchain=False, python_minify=False)


def get_pml_builder(args):
    """ Get Pml Builder """
    worktree = qisys.parsers.get_worktree(args, raises=False)
    pml_path = args.pml_path
    if pml_path.endswith(".mpml"):
        res = qipkg.metabuilder.MetaPMLBuilder(pml_path, worktree=worktree)
        configure_meta_builder(res, args)
    else:
        res = qipkg.builder.PMLBuilder(pml_path, worktree=worktree)
        configure_builder(res, args)
    return res


def configure_builder(pml_builder, args):
    """ Configure Builder """
    build_worktree = pml_builder.build_worktree
    if not build_worktree:
        return
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    build_worktree.build_config = build_config
    python_worktree = pml_builder.python_worktree
    config_name = build_config.build_directory(prefix="py")
    python_worktree.config = config_name


def configure_meta_builder(meta_builder, args):
    """ Configure Meta Builder """
    for pml_builder in meta_builder.pml_builders:
        configure_builder(pml_builder, args)
