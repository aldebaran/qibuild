## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import qisys
from qisys import ui


def generate_coverage_reports(project):
    """ Generate XML and HTML coverage reports
    """
    bdir = project.build_directory
    sdir = project.path
    formats = {"xml": ["--xml"],
               "html": ["--html", "--html-details"]}
    for fmt, opts in formats.iteritems():
        base_report = os.path.join(bdir, project.name + "." + fmt)
        cmd = ["gcovr",
                "--root", sdir,
                "--exclude", ".*test.*",
                "--exclude", ".*external.*",
                "--exclude", ".*example.*"] + opts + \
               ["--output", base_report]
        qisys.command.call(cmd, cwd=sdir, quiet=True)
        ui.info(ui.green, "*", ui.reset, "Generated", fmt.upper(),
                "coverage report in", ui.reset, ui.bold, base_report)
