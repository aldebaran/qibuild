## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisys import ui
from qisys.abstractbuilder import AbstractBuilder

class QiLinguistBuilder(AbstractBuilder):
    """ Builder for linguist projects
    """

    def __init__(self):
        self.projects = list()

    def configure(self, *args, **kwargs):
        for i, project in enumerate(self.projects):
            ui.info_count(i, len(self.projects), "Updating", project.name)
            project.update()

    def build(self, *args, **kwargs):
        for i, project in enumerate(self.projects):
            ui.info_count(i, len(self.projects), "Releasing", project.name)
            project.release(raises=kwargs.get("raises"))

    def install(self, dest):
        for i, project in enumerate(self.projects):
            ui.info_count(i, len(self.projects), "Installing", project.name)
            project.install(dest)
