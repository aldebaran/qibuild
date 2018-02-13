# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Apply changes from a manifest xml path.

Useful to check everything is ok before pushing the manifest

"""
import sys

import qisrc.parsers


def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("xml_path")


def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args)
    ok = git_worktree.check_manifest(args.xml_path)
    if not ok:
        sys.exit(1)
