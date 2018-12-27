#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Display the status of each project. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import glob
import time
import datetime

import qibuild.parsers
import qisys.parsers
from qisys import ui


def usage():
    """ Specific usage. """
    return """status [--all, -a] [projects...]"""


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser, positional=False)


def do(args):
    """ Main entry point. """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    for project in build_worktree.build_projects:
        ui.info(project.src)
        list_build_dir(project.path)


def list_build_dir(path):
    """ List all buildable directory. """
    bdirs = glob.glob(os.path.join(path, "build-*"))
    max_len = 0
    for bdir in bdirs:
        if len(bdir) > max_len:
            max_len = len(bdir)
    for bdir in bdirs:
        if os.path.isdir(bdir):
            ctim = time.time()
            ftim = os.path.getmtime(bdir)
            delta = ctim - ftim
            ddelta = datetime.timedelta(seconds=delta)
            todisplay = ""
            if ddelta.days > 0:
                todisplay = "%d days, %d hours" % \
                    (ddelta.days, ddelta.seconds / 3600)
            elif ddelta.seconds > 3600:
                todisplay = "%d hours" % (ddelta.seconds / 3600)
            else:
                todisplay = "%d minutes" % (ddelta.seconds / 60)
            pad = " " * (max_len - len(bdir))
            ui.info(" %s%s: (%s)" % (os.path.basename(bdir), pad, todisplay))
