## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Display info about the current git worktree

"""

from qisys import ui
import qisrc.parsers

import sys

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)

def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args)
    manifest = git_worktree.manifest
    ui.info(ui.green, "Manifest configured for",
            ui.reset, ui.bold, git_worktree.root, "\n",
            ui.reset, "url:   ", ui.bold, manifest.url, "\n",
            ui.reset, "branch:", ui.bold, manifest.branch)
    if manifest.groups:
        ui.info(ui.reset, "groups:", ui.bold, ", ".join(manifest.groups))
