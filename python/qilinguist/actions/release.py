## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Compile message catalog (PO file) to binary format (MO file) for each supported languages"""

import os

from qisys import ui
import qisys.parsers
import qilinguist.qigettext
import qilinguist.qtlinguist
import qilinguist.config
import qisrc

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)

def process_with_gettext(project):
    # get locale
    locale = qilinguist.config.get_locale_from_qiproject(project)
    domain = qilinguist.config.get_domain_from_qiproject(project)

    # get output directory
    base_output_dir = os.path.join(project.path, "po", "share", "locale", domain)
    # get input directory
    input_dir = os.path.join(project.path, "po")
    for l in locale:
        # get intput file
        input_file = os.path.join(project.path, "po", l + ".po")
        # get output file
        output_dir = os.path.join(base_output_dir, l, "LC_MESSAGES")
        output_file = domain + ".mo"
        qilinguist.qigettext.generate_mo_file(input_file, output_file, domain, input_dir, output_dir)

def process_with_qt(project):
    # get locale
    locale = qilinguist.config.get_locale_from_qiproject(project)

    # get output directory
    output_dir = os.path.join(project.path, "po")

    for l in locale:
        # get intput file
        input_file = os.path.join(project.path, "po", l + ".ts")
        # get output file
        output_file = l + ".qm"
        qilinguist.qtlinguist.generate_qm_file(input_file, output_file, output_dir)



def do(args):
  """Main entry point"""

  worktree = qisrc.open_worktree(args.worktree)
  projects = qisrc.cmdparse.projects_from_args(args, worktree)
  for project in projects:
      if not os.path.exists(project.qiproject_xml):
          ui.error("No qiproject.xml for project " + project.src)
          return

      tr_framework = qilinguist.config.get_tr_framework(project)

      if (tr_framework == "gettext"):
          process_with_gettext(project)
      elif (tr_framework == "qt"):
          process_with_qt(project)
