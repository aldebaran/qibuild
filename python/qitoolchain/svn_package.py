import qitoolchain.qipackage
import qisrc.svn

class SvnPackage(qitoolchain.qipackage.QiPackage):
    def __init__(self, name):
        super(SvnPackage, self).__init__(name)
        self.url = None
        self.revision = None
        self.svn = qisrc.svn.Svn(self.path)

    def update(self):
        cmd = ["update"]
        if self.revision:
            cmd.extend(["--revision", self.revision])
        self.svn.call(*cmd)

    def checkout(self):
        self.svn.call("checkout", self.url, ".")

    def commit_all(self):
        self.svn.commit_all("Update %s" % self.name)
