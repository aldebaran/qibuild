## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisys import ui
import qisys.error
import qisys.parsers


import qidoc.builder
from qidoc.worktree import DocWorkTree, new_doc_project

def build_doc_parser(parser):
    """ Add options used during the building of the documentation """
    group = parser.add_argument_group("doc build options")
    group.add_argument("--version")
    group.add_argument("--hosted", action="store_true", dest="hosted")
    group.add_argument("--local", action="store_false", dest="hosted")
    group.add_argument("--release", action="store_const", dest="build_type",
                       const="release")
    group.add_argument("--werror", action="store_true", dest="werror")
    group.add_argument("--no-warnings", action="store_true", dest="werror")
    group.add_argument("--spellcheck", action="store_true", dest="spellcheck")
    group.add_argument("-l", "--language", dest="language")
    parser.set_defaults(hosted=True, build_type="debug", werror=False,
                        spellcheck=False, language="en")

def get_doc_worktree(args):
    worktree = qisys.parsers.get_worktree(args)
    doc_worktree =  DocWorkTree(worktree)
    ui.info(ui.green, "Current doc worktree:", ui.reset,
            ui.bold, doc_worktree.root)
    return doc_worktree

def get_doc_projects(doc_worktree, args, default_all=False):
    parser = DocProjectParser(doc_worktree)
    return parser.parse_args(args, default_all=default_all)

def get_one_doc_project(doc_worktree, args):
    parser = DocProjectParser(doc_worktree)
    projects = parser.parse_args(args)
    if not len(projects) == 1:
        raise qisys.error.Error("This action can only work with one project")
    return projects[0]

def get_doc_builder(args):
    doc_worktree = get_doc_worktree(args)
    doc_project = get_one_doc_project(doc_worktree, args)
    doc_builder = qidoc.builder.DocBuilder(doc_worktree)
    doc_builder.set_base_project(doc_project.name)
    doc_builder.single = vars(args).get("single", False)
    doc_builder.version = vars(args).get("version")
    doc_builder.local = vars(args).get("hosted", True)
    doc_builder.build_type = vars(args).get("build_type")
    doc_builder.werror = vars(args).get("werror", False)
    doc_builder.spellcheck = vars(args).get("spellcheck", False)
    doc_builder.language = vars(args).get("language", "en")
    return doc_builder

##
# Implementation details

class DocProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a DocWorkTree """

    def __init__(self, doc_worktree):
        self.doc_worktree = doc_worktree
        self.doc_projects = doc_worktree.doc_projects

    def all_projects(self, args):
        return self.doc_projects

    def parse_no_project(self, args):
        """ Try to find the closest worktree project that
        matches the current directory

        """
        worktree = self.doc_worktree.worktree
        parser = qisys.parsers.WorkTreeProjectParser(worktree)
        worktree_projects = parser.parse_no_project(args)
        if not worktree_projects:
            raise CouldNotGuessProjectName()

        # WorkTreeProjectParser returns None or a list of one element
        worktree_project = worktree_projects[0]
        doc_project = new_doc_project(self.doc_worktree, worktree_project)
        if not doc_project:
            raise CouldNotGuessProjectName()

        return self.parse_one_project(args, doc_project.name)

    def parse_one_project(self, args, project_arg):
        """ Get one doc project given its name """

        project = self.doc_worktree.get_doc_project(project_arg, raises=True)
        return [project]

class CouldNotGuessProjectName(qisys.error.Error):
    def __str__(self):
        return """
Could not guess doc project name from current working directory
Please go inside a doc project, or specify the project name
on the command line
"""
