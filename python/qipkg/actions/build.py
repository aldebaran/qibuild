#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Build all the projects of the given pml file """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qipkg.parsers
import qibuild.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qipkg.parsers.pml_parser(parser)
    qibuild.parsers.cmake_build_parser(parser, with_build_parser=False)


def do(args):
    """ Main entry point """
    pml_builder = qipkg.parsers.get_pml_builder(args)
    pml_builder.build()
