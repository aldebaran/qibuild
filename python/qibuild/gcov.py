## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import qisys
from qisys import ui

def generate_coverage_reports(project, output_dir=None, exclude_patterns=None):
    """ Generate XML and HTML coverage reports
    """
    outdir = output_dir or os.path.join(project.sdk_directory, "coverage-results")
    sdir = project.path
    # Make sure output dir exists and is empty:
    qisys.sh.rm(outdir)
    qisys.sh.mkdir(outdir, recursive=True)
    formats = {"xml": ["--xml"],
               "html": ["--html", "--html-details"]}
    if exclude_patterns is None:
        exclude_patterns = [".*test.*", ".*external*", ".*example.*"]
    exclude_args = list()

    for exclude_pattern in exclude_patterns:
        exclude_args.extend(["--exclude", exclude_pattern])

    for fmt, opts in formats.iteritems():
        cmd = ["gcovr",
                "--root", sdir,
        ]
        # Add the build dir as argument for gcovr to find the .gcda files
        # even when using out-of-worktree builds:
        cmd.append(project.build_directory)
        cmd += exclude_args
        cmd += opts
        base_report = os.path.join(outdir, project.name + "." + fmt)
        cmd += ["--output", base_report]
        qisys.command.call(cmd, cwd=sdir, quiet=True)
        ui.info(ui.green, "*", ui.reset, "Generated", fmt.upper(),
                "coverage report in", ui.reset, ui.bold, base_report)
