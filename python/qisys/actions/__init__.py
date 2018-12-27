#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Common tools for actions """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

import qisys
import qisys.command
from qisys import ui


def foreach(projects, cmd, ignore_errors=True):
    """
    Execute the command on every project
    :param ignore_errors: whether to stop at first failure
    """
    errors = list()
    ui.info(ui.green, "Running `%s` on every project" % " ".join(cmd))
    for i, project in enumerate(projects):
        ui.info_count(i, len(projects), ui.blue, project.src)
        command = cmd[:]
        try:
            qisys.command.call(command, cwd=project.path)
        except qisys.command.CommandFailedException:
            if ignore_errors:
                errors.append(project)
                continue
            else:
                raise
    if not errors:
        return
    print()
    ui.info(ui.red, "Command failed on the following projects:")
    for project in errors:
        ui.info(ui.green, " * ", ui.reset, ui.blue, project.src)
    sys.exit(1)
