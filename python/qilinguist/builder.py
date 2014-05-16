## Copyright (c) 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisys.abstractbuilder import AbstractBuilder

class QiLinguistBuilder(AbstractBuilder):
    """ Builder for linguist projects
    """

    def __init__(self, linguist_worktree):
        self.linguist_worktree = linguist_worktree
        self.projects = list()

    def add_project(self, name):
        self.projects.append(self.linguist_worktree.get_linguist_project(name))

    def configure(self, *args, **kwargs):
        for project in self.projects:
            project.update()

    def build(self, *args, **kwargs):
        for project in self.projects:
            project.release()

    def install(self, dest):
        for project in self.projects:
            project.install(dest)
