#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Open the current documentation in a web browser. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import webbrowser

import qidoc.parsers
import qisys.sh
import qisys.command
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("-b", "--browser")
    parser.add_argument("-l", "--language")
    parser.set_defaults(language="en")


def do(args):
    """ Main Entry Point """
    doc_worktree = qidoc.parsers.get_doc_worktree(args)
    doc_project = qidoc.parsers.get_one_doc_project(doc_worktree, args)
    if doc_project.translated:
        doc_project.html_dir = os.path.join(doc_project.html_dir,
                                            args.language)
    index_html = doc_project.index_html
    if not os.path.exists(doc_project.index_html):
        mess = """ \
The doc project in {path} does no appear to have been built yet.
({index_html} does not exist.
Try running  `qidoc build`
"""
        mess = mess.format(path=doc_project.path, index_html=index_html)
        ui.error(mess)
        sys.exit(1)
    if sys.platform == "darwin":
        index_html = "file://" + index_html
    if args.browser:
        cmd = [args.browser, index_html]
        qisys.command.call(cmd)
    else:
        webbrowser.open(index_html)
