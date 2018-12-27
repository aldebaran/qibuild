#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.sh
import qisrc.svn
import qitoolchain.qipackage


class SvnPackage(qitoolchain.qipackage.QiPackage):
    """ QiPackage Managed by SubVersion """

    def __init__(self, name):
        """ SvnPackage Init """
        super(SvnPackage, self).__init__(name)
        self.url = None
        self.revision = None

    @property
    def svn(self):
        """ Return the SVN Instance """
        return qisrc.svn.Svn(self.path)

    def update(self):
        """ Run svn update with the appropriate revision """
        cmd = ["update"]
        if self.revision:
            cmd.extend(["--revision", self.revision])
        self.svn.call(*cmd)

    def checkout(self):
        """ Run svn checkout to create the package files """
        qisys.sh.mkdir(self.path, recursive=True)
        self.svn.call("checkout", self.url, ".", "--quiet")

    def commit_all(self):
        """ Commit all changes made to this package files """
        self.svn.commit_all("Update %s" % self.name)
