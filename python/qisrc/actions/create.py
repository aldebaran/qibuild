#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Create a new project """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisrc  # for QISRC_ROOT_DIR
import qisrc.templates
import qisys.parsers
from qisys import ui


def parse_params_arg(params_arg):
    """ Parse Params Arg """
    params = dict()
    args = params_arg.split(',')
    for arg in args:
        keyvalue = arg.split('=')
        params[keyvalue[0]] = keyvalue[1]
    return params


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("project_name",
                        help="The name of the project. "
                        "The project will be created in PWD/<name> ")
    parser.add_argument("-i", "--input", "--template-path", dest="template_path")
    parser.add_argument("--git", action="store_true",
                        help="Create a git repository.")
    parser.add_argument("-o", "--output", dest="output_dir")
    parser.add_argument("-p", "--params", action="append", type=parse_params_arg, dest="params",
                        help="Set parameters to be used to fill in the template, for example:"
                        "--params namespace=AL,domain=aldebaran.com")


def do(args):
    """" Create a new project """
    try:
        worktree = qisys.parsers.get_worktree(args)
    except qisys.worktree.NotInWorkTree:
        worktree = None
    template_kwargs = dict()
    if args.params is not None:
        for params in args.params:
            template_kwargs.update(params)
    template_kwargs["project_name"] = os.path.basename(args.project_name)
    output_dir = args.output_dir
    if not output_dir:
        output_dir = qisrc.templates.attached_lower(template_kwargs["project_name"])
        output_dir = os.path.join(os.getcwd(), output_dir)
    if os.path.exists(output_dir):
        raise Exception("%s already exists" % output_dir)
    template_path = args.template_path
    if not template_path:
        template_path = os.path.join(qisrc.QISRC_ROOT_DIR, "templates", "project")
    qisrc.templates.process(template_path, output_dir, **template_kwargs)
    if args.git:
        qisys.command.call(["git", "init"], cwd=output_dir)
        with open(os.path.join(output_dir, ".gitignore"), "w") as fp:
            fp.write("build-*\n")
        qisys.command.call(["git", "add", "."], cwd=output_dir)
        qisys.command.call(["git", "commit", "-m", "initial commit"], cwd=output_dir)
    ui.info(ui.green, "New project initialized in", ui.bold, output_dir)
    if worktree:
        worktree.add_project(output_dir)
        return worktree.get_project(output_dir)
    return None
