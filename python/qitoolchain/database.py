import os

from qisys import ui
from qisys.qixml import etree
import qisys.qixml
import qitoolchain.feed
import qitoolchain.qipackage

class DataBase(object):
    def __init__(self, name, db_path):
        self.name = name
        self.db_path = db_path
        self.packages = dict()
        self.load()
        self.cache_path = qisys.sh.get_cache_path("qi", "toolchains",
                                                  self.name)
        self.packages_path = qisys.sh.get_share_path("qi", "toolchains",
                                                     self.name)

    def load(self):
        """ Load the packages from the xml file """
        tree = qisys.qixml.read(self.db_path)
        for element in tree.findall("package"):
            to_add = qitoolchain.qipackage.from_xml(element)
            self.packages[to_add.name] = to_add

    def save(self):
        """ Save the packages in the xml file """
        root = etree.Element("toolchain")
        tree = etree.ElementTree(root)
        for package in self.packages.itervalues():
            element = etree.Element("package")
            element.set("name", package.name)
            if package.path:
                element.set("path", package.path)
            if package.version:
                element.set("version", package.version)
            if package.url:
                element.set("url", package.url)
            root.append(element)
        qisys.qixml.write(tree, self.db_path)

    def add_package(self, package):
        self.packages[package.name] = package

    def remove_package(self, name):
        if name not in self.packages:
            raise Exception("No such package: %s" % name)
        del self.packages[name]

    def get_package_path(self, name):
        if name in self.packages:
            return self.packages[name].path

    def get_package(self, name, raises=True):
        res = self.packages.get(name)
        if res is None:
            if raises:
                raise Exception("No such package: %s" % name)
        return res

    def solve_deps(self, packages, dep_types=None):
        to_sort = dict()
        for package in self.packages.values():
            package.load_deps()
            deps = set()
            if "build" in dep_types:
                deps.update(package.build_depends)
            if "runtime" in dep_types:
                deps.update(package.run_depends)
            if "test" in dep_types:
                deps.update(package.test_depends)
            to_sort[package.name] = deps
        sorted_names = qisys.sort.topological_sort(to_sort, [x.name for x in packages])
        res = list()
        for name in sorted_names:
            if name in self.packages:
                res.append(self.packages[name])
        return res

    def update(self, feed):
        feed_parser = qitoolchain.feed.ToolchainFeedParser()
        feed_parser.parse(feed)
        remote_packages = feed_parser.get_packages()
        local_packages = self.packages.values()
        to_add = list()
        to_remove = list()
        for remote_package in remote_packages:
            if remote_package in local_packages:
                continue
            to_add.append(remote_package)
        for local_package in local_packages:
            if local_package not in remote_packages:
                to_remove.append(local_package)

        for package in to_remove:
            self.remove_package(package.name)
        for package in to_add:
            self.handle_package(package, feed)
            self.packages[package.name] = package

        self.save()

    def handle_package(self, package, feed):
        if package.url:
            if package.url.startswith("svn://"):
                self.handle_svn_package(package)
            else:
                self.download_package(package)
        if package.directory:
            self.handle_local_package(package, feed)
        if package.toolchain_file:
            self.handle_toochain_file(package, feed)

    def handle_svn_package(self, package):
        dest = os.path.join(self.packages_path, package.name)
        revision = package.version
        if os.path.exists(dest):
            cmd = ["svn", "update", "--revision", revision]
            qisys.command.call(cmd, cwd=dest)
        else:
            qisys.sh.mkdir(self.packages_path, recursive=True)
            cmd = ["svn", "checkout", "--revision", revision, package.url, package.name]
            qisys.command.call(cmd, cwd=self.packages_path)
        package.path = dest

    def handle_local_package(self, package, feed):
        directory = package.directory
        feed_root = os.path.dirname(feed)
        package_path = os.path.join(feed_root, directory)
        package_path = qisys.sh.to_native_path(package_path)
        package.path = package_path

    def handle_toochain_file(self, package, feed):
        toolchain_file = package.toolchain_file
        package_path = package.path
        # toolchain_file can be an url too
        if not "://" in toolchain_file:
            package.toolchain_file = os.path.join(package.path, toolchain_file)
        else:
            tc_file = qisys.remote.download(toolchain_file, package.path)
            package.toolchain_file = tc_file

        if package.sysroot:
            package.sysroot = os.path.join(package.path, package.sysroot)
        if package.cross_gdb:
            package.cross_gdb = os.path.join(package.path, package.cross_gdb)

    def remove(self):
        qisys.sh.rm(self.packages_path)

    def clean_cache(self):
        qisys.sh.rm(self.cache_path)

    def download_package(self, package):
        archive = qisys.remote.download(package.url, self.cache_path,
                                        message = (ui.green, "Downloading",
                                                   ui.reset, ui.blue, package.url))
        dest = os.path.join(self.packages_path, "%s-%s" % \
                            (package.name, package.version))
        ui.info(ui.green, "Extracting",
                ui.reset, ui.blue, package.name, package.version)
        qisys.archive.extract(archive, self.packages_path, strict_mode=False)
        package.path = dest
