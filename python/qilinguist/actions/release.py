## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Compile binary translations files

"""

import os

import qisys.parsers
import qilinguist.parsers

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def do(args):
  """Main entry point"""
  linguist_worktree = qilinguist.parsers.get_linguist_worktree(args)
  projects = qilinguist.parsers.get_linguist_projects(linguist_worktree, args)
  for project in projects:
      project.release()
