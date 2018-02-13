# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import os
import sys
import re
import zipfile
import shlex

from qisys.qixml import etree
import qisys.version
import qisrc.license
import qibuild.deps


class QiPackage(object):  # pylint: disable=too-many-instance-attributes
    """ Binary package for use with qibuild.

    Package names are unique in a given toolchain.
    path is None until the package is added to a database

    """

    def __init__(self, name, version=None, path=None):
        self.name = name
        self.version = version
        self.target = None
        self.host = None
        self.path = path
        self.url = None
        self.directory = None
        self.toolchain_file = None
        self.sysroot = None
        self.cross_gdb = None
        self.build_depends = set()
        self.run_depends = set()
        self.test_depends = set()
        self._post_add = None
        self.subpkg = None

    @property
    def license(self):
        """ The license of the package """
        package_xml = os.path.join(self.path, "package.xml")
        return qisrc.license.read_license(package_xml)

    @license.setter
    def license(self, value):
        package_xml = os.path.join(self.path, "package.xml")
        qisrc.license.write_license(package_xml, value)

    def load_deps(self):
        """ Parse package.xml, set the dependencies """
        package_xml = os.path.join(self.path, "package.xml")
        if os.path.exists(package_xml):
            xml_root = qisys.qixml.read(package_xml)
            qibuild.deps.read_deps_from_xml(self, xml_root)

    def to_xml(self):
        """ Return an ``etree.Element`` representing this package """
        element = etree.Element("package")
        element.set("name", self.name)
        if self.path:
            element.set("path", self.path)
        if self.version:
            element.set("version", self.version)
        if self.url:
            element.set("url", self.url)
        if self.toolchain_file:
            element.set("toolchain_file", self.toolchain_file)
        if self.sysroot:
            element.set("sysroot", self.sysroot)
        if self.cross_gdb:
            element.set("cross_gdb", self.cross_gdb)
        if self.subpkg:
            element.set("subpkg", self.subpkg)
        return element

    def install(self, destdir, components=None, release=True):
        """ Install the given components of the package to the given destination

        Will read

        * ``install_manifest_<component>.txt`` for each component if the file exists
        * ``<component>.mask`` to exclude files matching some regex if the mask exists
        * if none exits, will apply the ``qisys.sh.is_runtime`` filter when
          installing *runtime* component

        Note that when installing 'test' component, only the
        install_manifest_test.txt manifest file will be read

        """
        if self.subpkg:
            return list()
        if not components:
            return self._install_all(destdir)
        installed_files = list()
        for component in components:
            installed_for_component = self._install_component(component,
                                                              destdir, release=release)
            installed_files.extend(installed_for_component)
        return installed_files

    def _install_all(self, destdir):
        def filter_fun(x):
            return x != "package.xml"
        return qisys.sh.install(self.path, destdir, filter_fun=filter_fun)

    def _install_component(self, component, destdir, release=True):
        installed_files = list()
        manifest_name = "install_manifest_%s.txt" % component
        if not release and sys.platform.startswith("win"):
            manifest_name = "install_manifest_%s_debug.txt" % component
        manifest_path = os.path.join(self.path, manifest_name)
        if not os.path.exists(manifest_path):
            if component == "test":
                # tests can only be listed in an install manifest
                return list()
            mask = self._read_install_mask(component)
            if release:
                mask.extend(self._read_install_mask("release"))
            if not mask and component == "runtime":
                # retro-compat
                def filter_fun(x):
                    return qisys.sh.is_runtime(x) and x != "package.xml"
                return qisys.sh.install(self.path, destdir, filter_fun=filter_fun)

            # avoid install masks and package.xml
            mask.append(r"exclude .*\.mask")
            mask.append(r"exclude package\.xml")
            return self._install_with_mask(destdir, mask)
        else:
            with open(manifest_path, "r") as fp:
                lines = fp.readlines()
                for line in lines:
                    line = line.strip()
                    src = os.path.join(self.path, line)
                    dest = os.path.join(destdir, line)
                    qisys.sh.install(src, dest)
                    installed_files.append(line)
            return installed_files

    def _read_install_mask(self, mask_name):
        mask_path = os.path.join(self.path, mask_name + ".mask")
        if not os.path.exists(mask_path):
            return list()
        with open(mask_path, "r") as fp:
            mask = fp.readlines()
            mask = [x.strip() for x in mask]
            # remove empty lines and comments:
            mask = [x for x in mask if x != ""]
            mask = [x for x in mask if not x.startswith("#")]
            for line in mask:
                if not line.startswith(("include ", "exclude ")):
                    mess = "Bad mask in %s\n" % mask_path
                    mess += line + "\n"
                    mess += "line should start with 'include' or 'exclude'"
                    raise Exception(mess)
            return mask

    def _install_with_mask(self, destdir, mask):
        def get_match(line, src):
            words = line.split()
            regex = " ".join(words[1:])
            return re.match(regex, src)

        def filter_fun(src):
            src = qisys.sh.to_posix_path(src)
            positive_regexps = [x for x in mask if x.startswith("include")]
            negative_regexps = [x for x in mask if x.startswith("exclude")]
            for line in positive_regexps:
                match = get_match(line, src)
                if match:
                    return True
            for line in negative_regexps:
                match = get_match(line, src)
                if match:
                    return False
            return True

        return qisys.sh.install(self.path, destdir, filter_fun=filter_fun)

    def load_package_xml(self):
        """ Load metadata from package.xml

        Assume self.path is set: must be called after
        the package has been added to a toolchain

        """
        package_xml = os.path.join(self.path, "package.xml")
        if not os.path.exists(package_xml):
            return
        root = qisys.qixml.read(package_xml).getroot()
        self.toolchain_file = root.get("toolchain_file")
        self.sysroot = root.get("sysroot")
        self.cross_gdb = root.get("cross_gdb")
        self._post_add = root.get("post-add")

    def reroot_paths(self):
        """ Make sure all the paths are absolute.
        Assume self.path is set: must be called after
        the package has been added to a toolchain

        """
        if self.toolchain_file:
            self.toolchain_file = os.path.join(self.path, self.toolchain_file)
        if self.sysroot:
            self.sysroot = os.path.join(self.path, self.sysroot)
        if self.cross_gdb:
            self.cross_gdb = os.path.join(self.path, self.cross_gdb)

    def post_add(self):
        """ Run the post-add script if it exists.

        Raises:
            * CommandFailedException if the post-add script fails
        """

        if not self._post_add:
            return

        # Make sure the script is found in the package directory
        post_add_cmd = shlex.split(self._post_add)
        post_add_cmd[0] = os.path.join(self.path, post_add_cmd[0])

        qisys.command.call(post_add_cmd, cwd=self.path)

    def __repr__(self):
        return "<Package %s %s>" % (self.name, self.version)

    def __str__(self):
        if self.version:
            res = "%s-%s" % (self.name, self.version)
        else:
            res = self.name
        if self.path:
            res += " in %s" % self.path
        return res

    def __cmp__(self, other):
        if self.name == other.name:
            if self.version is None and other.version is not None:
                return -1
            if self.version is not None and other.version is None:
                return 1
            if self.version is None and other.version is None:
                return 0
            return qisys.version.compare(self.version, other.version)
        else:
            return cmp(self.name, other.name)


def from_xml(element):
    name = element.get("name")
    if not name:
        raise Exception("missing 'name' attribute")
    url = element.get("url")
    if element.tag == "svn_package":
        import qitoolchain.svn_package
        res = qitoolchain.svn_package.SvnPackage(name)
        res.revision = element.get("revision")
    else:
        res = QiPackage(name)
    res.url = url
    res.version = element.get("version")
    res.path = element.get("path")
    res.directory = element.get("directory")
    res._post_add = element.get("post-add")  # pylint: disable=protected-access
    res.subpkg = element.get("subpkg")
    if res.url and res.directory:
        mess = """\
Bad configuration for package %s. 'directory' and 'url' are
mutually exclusive
"""
        raise Exception(mess % name)
    res.toolchain_file = element.get("toolchain_file")
    res.sysroot = element.get("sysroot")
    res.cross_gdb = element.get("cross_gdb")
    res.target = element.get("target")
    res.host = element.get("host")
    qibuild.deps.read_deps_from_xml(res, element)
    return res


def from_archive(archive_path):
    archive = zipfile.ZipFile(archive_path)
    xml_data = archive.read("package.xml")
    element = etree.fromstring(xml_data)
    return from_xml(element)


def extract(archive_path, dest):
    if archive_path.endswith((".tar.gz", ".tbz2")):
        return _extract_legacy(archive_path, dest)
    with zipfile.ZipFile(archive_path) as archive:
        if "package.xml" in archive.namelist():
            return _extract_modern(archive_path, dest)

        return _extract_legacy(archive_path, dest)


def _extract_modern(archive_path, dest):
    return qisys.archive.extract(archive_path, dest, strict_mode=False)


def _extract_legacy(archive_path, dest):
    dest = qisys.sh.to_native_path(dest)
    algo = qisys.archive.guess_algo(archive_path)
    extract_dest = os.path.dirname(dest)
    extract_path = qisys.archive.extract(archive_path, extract_dest, algo=algo)
    extract_path = os.path.abspath(extract_path)
    if extract_path != dest:
        qisys.sh.mkdir(dest, recursive=True)
        qisys.sh.rm(dest)
        qisys.sh.mv(extract_path, dest)
        qisys.sh.rm(extract_path)
        return dest

    return extract_path
