## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" List the qidoc projects

"""

import operator

from qisys import ui
import qisys.parsers
import qidoc.parsers

import qidoc.convert

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def do(args):
    doc_worktree = qidoc.parsers.get_doc_worktree(args)
    doc_projects = doc_worktree.doc_projects
    if not doc_projects:
        return
    ui.info(ui.green, "qidoc projects in:", ui.blue, doc_worktree.root)
    max_name = max(len(x.name) for x in doc_projects)
    ui.info()
    for doc_type in ["doxygen", "sphinx"]:
        matching_projects = [x for x in doc_projects if x.doc_type == doc_type]
        matching_projects.sort(key=operator.attrgetter("name"))
        if not matching_projects:
            continue
        ui.info(ui.green, doc_type.capitalize(),
                "projects")
        for project in matching_projects:
            ui.info(ui.green, " * ", ui.blue, project.name.ljust(max_name),
                    "  ", ui.reset, project.path)
        ui.info()
