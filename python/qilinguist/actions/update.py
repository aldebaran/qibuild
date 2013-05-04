## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Update message catalog (PO file) from a message template (POT file)"""

import os

from qisys import ui
import qisys.worktree
import qilinguist.qigettext
import qilinguist.qtlinguist
import qilinguist.config

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def extract_pot_file(project, domain):
    """Extract sentence from source file and generate POT file"""
    # check if POTFILES.in exists
    potfiles_in_path = os.path.join(project.path, "po", "POTFILES.in")
    if not os.path.exists(potfiles_in_path):
        ui.error("No po/POTFILES.in for project", project.src)
        return

    # get input files and directory
    input_dir, input_files = qilinguist.config.parse_potfiles_in(project.path,
                                                                 potfiles_in_path)

    # get input directory
    if input_dir:
        input_dir = os.path.join(project.path, input_dir)
    else:
        input_dir = project.path

    # get output file
    output = domain + ".pot"

    # get output directory
    output_dir = os.path.join(project.path, "po")
    qisys.sh.mkdir(output_dir, True)

    # Generate pot file
    qilinguist.qigettext.generate_pot_file(domain, input_files, output,
            input_dir=input_dir, output_dir=output_dir)

def update_po_file(project, domain, locale):
    """Update PO file from POT"""
    # get input file
    input_file = os.path.join(project.path, "po", domain + ".pot")
    if not os.path.exists(input_file):
        ui.error("No pot file found. Maybe no translatable strings were found?")
        return

    # get input directory
    input_dir = os.path.join(project.path, "po")
    # get udapte directory
    update_dir = os.path.join(project.path, "po")
    # get update file
    update_file = locale + ".po"
    # Update
    qilinguist.qigettext.update_po_file(input_file, update_file, input_dir, update_dir)

def generate_po_file(project, domain, locale):
    """Generate PO file"""
    # get input file
    input_file = os.path.join(project.path, "po", domain + ".pot")
    if not os.path.exists(input_file):
        ui.error("No pot file found. Maybe no translatable strings were found?")
        return

    # get output file
    output_file = os.path.join(project.path, "po", locale + ".po")
    # generate PO file
    qilinguist.qigettext.generate_po_file(input_file, output_file, locale)

def process_with_gettext(project):
    # get domain
    domain = qilinguist.config.get_domain_from_qiproject(project)
    # get locale
    locale = qilinguist.config.get_locale_from_qiproject(project)

    # extract sentence and generate POT file
    extract_pot_file(project, domain)

    # for each locale generate or update PO file
    for l in locale:
        # check if PO file exists
        output_file = os.path.join(project.path, "po", l + ".po")
        if os.path.exists(output_file):
            # Update PO file if it exists
            update_po_file(project, domain, l)
        else:
            # generate PO file if it doesn't exist
            generate_po_file(project, domain, l)

def process_with_qt(project):
    potfiles_in_path = os.path.join(project.path, "po", "POTFILES.in")
    if not os.path.exists(potfiles_in_path):
        ui.error("No po/POTFILES.in for project", project.src)
        return

    # get locale
    linguas = qilinguist.config.get_locale_from_qiproject(project)

    # get input file
    input_files = qilinguist.config.get_relative_file_path_potfiles_in(project,
            potfiles_in_path)

    output_file = list()
    for l in linguas:
        # get output file
        output_file.append(l + ".ts")

    output_dir = os.path.join(project.path, "po")
    qilinguist.qtlinguist.generate_ts_files(input_files, output_file, output_dir)


def do(args):
  """Main entry point"""
  linguist_worktree = qilinguist.parsers.get_linguist_worktree(args)
  projects = qilinguist.parsers.get_linguist_projects(linguist_worktree, args)
  for project in projects:
      qiproject_path = project.qiproject_xml
      if not os.path.exists(qiproject_path):
          ui.error("No qiproject.xml for project", project.src)
          return
      tr_framework = qilinguist.config.get_tr_framework(project)
      if (tr_framework == "gettext"):
          process_with_gettext(project)
      elif (tr_framework == "qt"):
          process_with_qt(project)
