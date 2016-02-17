## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisys.test.conftest import *

import qisys.qixml
from qisys.qixml import etree
import qisys.remote
import qibuild.config
import qibuild.deps
import qitoolchain
import qitoolchain.qipackage
import qitoolchain.database
import qitoolchain.toolchain

class Toolchains():
    """ A class to help qitoolchain testing """
    def __init__(self):
        tmpdir = tempfile.mkdtemp(prefix="test-qitoolchain")
        # /tmp is a symlink on mac, leading to all kind of "interesting"
        # problems
        # pylint: disable-msg=E1101
        self.tmp = py.path.local(tmpdir).realpath()

    def clean(self):
        self.tmp.remove()

    def create(self, name):
        toolchain = qitoolchain.toolchain.Toolchain(name)
        return toolchain

    def add_package(self, name, package_name, package_version="r1",
                    build_depends=None, run_depends=None, test_depends=None,
                    host_depends=None):
        toolchain = qitoolchain.get_toolchain(name)
        package_path = self.tmp.mkdir(package_name)
        package = qitoolchain.qipackage.QiPackage(package_name, package_version)
        package.path = package_path.strpath

        # Make sure self.*_depends are sets
        for dep_type in ["build", "run", "test", "host"]:
            attr_name = "%s_depends" % dep_type
            value = locals()[attr_name]
            if value:
                setattr(package, attr_name, set(value))
            else:
                setattr(package, attr_name, set())

        package.write_package_xml()
        toolchain.add_package(package)
        return package

class TestFeed():
    def __init__(self, tmp):
        self.tmp = tmp
        self.packages_path = tmp.ensure("packages", dir=True)
        self.feed_xml = tmp.join("feed.xml")
        self.feed_xml.write("<toolchain/>")
        self.url = qisys.remote.local_url(self.feed_xml.strpath)

    def add_package(self, package, with_path=True, with_url=True):
        this_dir = os.path.dirname(__file__)
        this_dir = qisys.sh.to_native_path(this_dir)
        package_path = self.tmp.join("packages")
        package_path.ensure("lib", "lib%s.so" % package.name, file=True)
        package_path.ensure("include", "%s.h" % package.name, file=True)
        package_xml = package_path.join("package.xml")
        package_xml.write("""
<package name="%s" version="%s" />
""" % (package.name, package.version))
        archive_name = "%s-%s" % (package.name, package.version)
        output = package_path.join(archive_name + ".zip")
        archive = qisys.archive.compress(package_path.strpath, flat=True,
                                         output=output.strpath)

        if with_path:
            package.path = archive
        if with_url:
            base_url = self.url.replace("feed.xml", "")
            package.url = base_url + "/packages/%s.zip" % archive_name
        tree = qisys.qixml.read(self.feed_xml.strpath)
        root = tree.getroot()
        package_elem = package.to_xml()
        root.append(package_elem)
        qisys.qixml.write(tree, self.feed_xml.strpath)
        return package

    def add_svn_package(self, package):
        tree = qisys.qixml.read(self.feed_xml.strpath)
        root = tree.getroot()
        svn_elem = etree.SubElement(root, "svn_package")
        svn_elem.set("name", package.name)
        svn_elem.set("url", package.url)
        if package.revision:
            svn_elem.set("revision", package.revision)
        qisys.qixml.write(tree, self.feed_xml.strpath)

    def remove_package(self, name):
        tree = qisys.qixml.read(self.feed_xml.strpath)
        root = tree.getroot()
        for elem in root.findall("package"):
            if elem.get("name") == name:
                root.remove(elem)
        qisys.qixml.write(tree, self.feed_xml.strpath)

# pylint: disable-msg=E1101
@pytest.fixture
def feed(tmpdir):
    res = TestFeed(tmpdir)
    return res

@pytest.fixture
def toolchain_db(tmpdir):
    db_path = tmpdir.join("toolchain.xml")
    db_path.write("<toolchain />")
    db = qitoolchain.database.DataBase("bar", db_path.strpath)
    return db

# pylint: disable-msg=E1101
@pytest.fixture
def toolchains(request):
    res = Toolchains()
    request.addfinalizer(res.clean)
    return res

# pylint: disable-msg=E1101
@pytest.fixture
def qitoolchain_action(cd_to_tmpdir):
    res = QiToolchainAction()
    return res

# pylint: disable-msg=E1101
@pytest.fixture
def fake_ctc():
    toolchain = qitoolchain.toolchain.Toolchain("fake-ctc")
    this_dir= os.path.dirname(__file__)
    toolchain.update(feed_location=os.path.join(this_dir, "fakectc", "toolchain.xml"))
    qibuild.config.add_build_config("fake-ctc", toolchain="fake-ctc")
    return toolchain

class QiToolchainAction(TestAction):
    def __init__(self):
        super(QiToolchainAction, self).__init__("qitoolchain.actions")

    def get_test_package(self, name):
        # FIXME: handle mac, windows
        this_dir = os.path.dirname(__file__)
        return os.path.join(this_dir, "packages", name + ".zip")
