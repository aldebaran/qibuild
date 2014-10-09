import qitoolchain.qipackage
import qisrc.svn

class SvnPackage(qitoolchain.qipackage.QiPackage):
    """ A ``QiPackage`` managed by subversion """

    def __init__(self, name):
        super(SvnPackage, self).__init__(name)
        self.url = None
        self.revision = None
        self.svn = qisrc.svn.Svn(self.path)

    def update(self):
        """ Run ``svn update`` with the appropriate revision """
        cmd = ["update"]
        if self.revision:
            cmd.extend(["--revision", self.revision])
        self.svn.call(*cmd)

    def checkout(self):
        """ Run ``svn checkout`` to create the package files """
        self.svn.call("checkout", self.url, ".")

    def commit_all(self):
        """ Commit all changes made to this package files """
        self.svn.commit_all("Update %s" % self.name)
