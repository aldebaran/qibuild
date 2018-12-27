#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qisys import ui
from qisys.abstractbuilder import AbstractBuilder


class QiLinguistBuilder(AbstractBuilder):
    """ Builder for linguist projects """

    def __init__(self):
        """ QiLinguistBuilder Init """
        super(QiLinguistBuilder, self).__init__(self.__class__.__name__)
        self.projects = list()

    def configure(self, *args, **kwargs):
        """ Configure """
        for i, project in enumerate(self.projects):
            ui.info_count(i, len(self.projects), "Updating", project.name)
            project.update()

    def build(self, *args, **kwargs):
        """ Build """
        for i, project in enumerate(self.projects):
            ui.info_count(i, len(self.projects), "Releasing", project.name)
            project.release(raises=kwargs.get("raises"))

    def install(self, dest, *args, **kwargs):
        """ Install """
        for i, project in enumerate(self.projects):
            ui.info_count(i, len(self.projects), "Installing", project.name)
            project.install(dest)
