# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import qisys.parsers
import qibuild.parsers
import qipy.worktree
import qipy.python_builder


def get_python_worktree(args):
    worktree = qisys.parsers.get_worktree(args)
    build_worktree = qibuild.parsers.get_build_worktree(args, verbose=False)
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    config_name = build_config.build_directory(prefix="py")
    python_worktree = qipy.worktree.PythonWorkTree(worktree)
    python_worktree.config = config_name
    return python_worktree


def get_python_projects(python_worktree, args, default_all=False):
    parser = PythonProjectParser(python_worktree)
    return parser.parse_args(args, default_all=default_all)


def get_one_python_project(python_worktree, args):
    parser = PythonProjectParser(python_worktree)
    projects = parser.parse_args(args)
    if not len(projects) == 1:
        raise Exception("This action can only work with one project")
    return projects[0]


def get_python_builder(args, verbose=True):
    python_worktree = get_python_worktree(args)
    build_worktree = qibuild.parsers.get_build_worktree(args, verbose=verbose)
    python_builder = qipy.python_builder.PythonBuilder(python_worktree,
                                                       build_worktree)
    return python_builder


class PythonProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a PythonWorkTree """

    def __init__(self, python_worktree):
        super(PythonProjectParser, self).__init__()
        self.python_worktree = python_worktree
        self.python_projects = python_worktree.python_projects

    def all_projects(self, args):
        return self.python_projects

    def parse_no_project(self, args):
        """ Try to find the closest worktree project that
        matches the current directory

        """
        worktree = self.python_worktree.worktree
        parser = qisys.parsers.WorkTreeProjectParser(worktree)
        worktree_projects = parser.parse_no_project(args)
        if not worktree_projects:
            raise CouldNotGuessProjectName()

        # WorkTreeProjectParser returns None or a list of one element
        worktree_project = worktree_projects[0]
        python_project = qipy.worktree.new_python_project(self.python_worktree,
                                                          worktree_project)
        if not python_project:
            raise CouldNotGuessProjectName()

        return self.parse_one_project(args, python_project.name)

    def parse_one_project(self, args, project_arg):
        """ Get one python project given its name """

        project = self.python_worktree.get_python_project(project_arg, raises=True)
        return [project]


class CouldNotGuessProjectName(Exception):
    def __str__(self):
        return """
Could not guess python project name from current working directory
Please go inside a python project, or specify the project name
on the command line
"""
