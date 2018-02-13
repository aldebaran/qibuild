# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import qisys.sh
import qisys.parsers
import qilinguist.builder

from qilinguist.worktree import LinguistWorkTree, new_linguist_project
from qilinguist.pml_translator import new_pml_translator


def get_linguist_worktree(args):
    worktree = qisys.parsers.get_worktree(args, raises=False)
    if worktree:
        return LinguistWorkTree(worktree)

    return None


def get_linguist_projects(args, default_all=False):
    worktree = get_linguist_worktree(args)
    project_args = args.projects
    pml_paths = list()
    project_names = list()
    for arg in project_args:
        if arg.endswith(".pml"):
            pml_paths.append(qisys.sh.to_native_path(arg))
        else:
            if worktree:
                project_names.append(arg)
            else:
                raise Exception("Cannot use project names when running "
                                "outside a worktree")
    if not worktree and not pml_paths:
        raise Exception("You should specify at least a pml path when running "
                        "outside a worktree")
    res = list()
    if worktree:
        args.projects = project_names
        parser = LinguistProjectParser(worktree)
        try:
            res.extend(parser.parse_args(args, default_all=default_all))
        except CouldNotGuessProjectName:
            pass

    res.extend(get_pml_projects(pml_paths))
    return res


def get_pml_projects(pml_paths):
    res = list()
    for pml_path in pml_paths:
        res.append(new_pml_translator(pml_path))
    return res


def get_linguist_builder(args, with_projects=True):
    __worktree = get_linguist_worktree(args)  # pylint: disable=unused-variable
    builder = qilinguist.builder.QiLinguistBuilder()
    if with_projects:
        projects = get_linguist_projects(args)
        builder.projects = projects
    return builder


##
# Implementation details

class LinguistProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a LinguistWorkTree """

    def __init__(self, linguist_worktree):
        super(LinguistProjectParser, self).__init__()
        self.linguist_worktree = linguist_worktree
        self.linguist_projects = linguist_worktree.linguist_projects

    def all_projects(self, args):
        return self.linguist_projects

    def parse_no_project(self, args):
        """ Try to find the closest worktree project that
        matches the current directory

        """
        worktree = self.linguist_worktree.worktree
        parser = qisys.parsers.WorkTreeProjectParser(worktree)
        worktree_projects = parser.parse_no_project(args)
        if not worktree_projects:
            raise CouldNotGuessProjectName()

        # WorkTreeProjectParser returns None or a list of one element
        worktree_project = worktree_projects[0]
        linguist_project = new_linguist_project(self.linguist_worktree,
                                                worktree_project)
        if not linguist_project:
            raise CouldNotGuessProjectName()

        return self.parse_one_project(args, linguist_project.name)

    def parse_one_project(self, args, project_arg):
        """ Get one linguist project given its name """

        project = self.linguist_worktree.get_linguist_project(project_arg,
                                                              raises=True)
        return [project]


class CouldNotGuessProjectName(Exception):
    def __str__(self):
        return """
Could not guess linguist project name from current working directory
Please go inside a translatable project, or specify the project name
on the command line
"""
