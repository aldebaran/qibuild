#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Deploy a complete package on the robot.
This uses rsync to be fast.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.sh
import qisys.parsers
import qipkg.parsers


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.deploy_parser(parser)
    qipkg.parsers.pml_parser(parser)


def do(args):
    """ Main entry point. """
    urls = qisys.parsers.get_deploy_urls(args)
    pml_builder = qipkg.parsers.get_pml_builder(args)
    pml_builder.install(pml_builder.stage_path)
    for url in urls:
        pml_builder.deploy(url)
