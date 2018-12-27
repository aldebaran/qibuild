#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Generate XML and HTML coverage reports """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys
from qisys import ui


def generate_coverage_reports(project, output_dir=None):
    """ Generate XML and HTML coverage reports  """
    outdir = output_dir or os.path.join(project.sdk_directory, "coverage-results")
    sdir = project.path
    # Make sure output dir exists and is empty:
    qisys.sh.rm(outdir)
    qisys.sh.mkdir(outdir, recursive=True)
    formats = {"xml": ["--xml"],
               "html": ["--html", "--html-details"]}
    for fmt, opts in formats.items():
        base_report = os.path.join(outdir, project.name + "." + fmt)
        cmd = ["gcovr",
               "--root", sdir,
               "--exclude", ".*test.*",
               "--exclude", ".*external.*",
               "--exclude", ".*example.*"] + opts + \
            ["--output", base_report]
        qisys.command.call(cmd, cwd=sdir, quiet=True)
        ui.info(ui.green, "*", ui.reset, "Generated", fmt.upper(),
                "coverage report in", ui.reset, ui.bold, base_report)
