#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Deploy python projects to a remote location """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.sh
import qisys.command
import qisys.parsers
import qibuild.parsers
import qipy.parsers
import qipy.worktree


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    qisys.parsers.deploy_parser(parser)


def do(args):
    """ Main Entry Point """
    python_builder = qipy.parsers.get_python_builder(args)
    python_worktree = python_builder.python_worktree
    projects = qipy.parsers.get_python_projects(python_worktree, args)
    python_builder.projects = projects
    urls = qisys.parsers.get_deploy_urls(args)
    for url in urls:
        python_builder.deploy(url)
