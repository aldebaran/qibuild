## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.sh
import qitoolchain.qipackage
import qisrc.svn

class SvnPackage(qitoolchain.qipackage.QiPackage):
    """ A ``QiPackage`` managed by subversion """

    def __init__(self, name):
        super(SvnPackage, self).__init__(name)
        self.url = None
        self.revision = None

    @property
    def svn(self):
        return qisrc.svn.Svn(self.path)

    def update(self):
        """ Run ``svn update`` with the appropriate revision """
        cmd = ["update"]
        if self.revision:
            cmd.extend(["--revision", self.revision])
        self.svn.call(*cmd)

    def checkout(self):
        """ Run ``svn checkout`` to create the package files """
        qisys.sh.mkdir(self.path, recursive=True)
        self.svn.call("checkout", self.url, ".", "--quiet")

    def commit_all(self):
        """ Commit all changes made to this package files """
        self.svn.commit_all("Update %s" % self.name)
