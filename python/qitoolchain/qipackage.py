## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import sys
import re
import zipfile

from qisys import ui
from qisys.qixml import etree
import qisys.error
import qisys.version
import qisrc.license
import qibuild.deps

class QiPackage(object):
    """ Binary package for use with qibuild.

    Package names are unique in a given toolchain.
    path is None until the package is added to a database

    """

    _properties = ("name", "version", "url",
                   "path", "directory",
                   "target", "host",
                   "toolchain_file", "sysroot", "cross_gdb")

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
        qibuild.deps.dump_deps_to_xml(self, element)
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
            if not mask and component=="runtime":
                # retro-compat
                def filter_fun(x):
                    return qisys.sh.is_runtime(x) and x != "package.xml"
                return qisys.sh.install(self.path, destdir,
                                        filter_fun=filter_fun)
            else:
                # avoid install masks and package.xml
                mask.append("exclude .*\.mask")
                mask.append("exclude package\.xml")
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
                    raise qisys.error.Error(mess)
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

    def load_package_xml(self, element=None):
        """ Load metadata from package.xml

        Assume self.path is set: must be called after
        the package has been added to a toolchain

        """
        package_xml = None
        if element is None:
            package_xml = os.path.join(self.path, "package.xml")
            if os.path.exists(package_xml):
                element = qisys.qixml.read(package_xml).getroot()
            else:
                package_xml = None
                element = etree.Element("package")

        ok = True
        for property in self._properties:
            if not self._set_property(package_xml, property, element):
                ok = False

        if not ok:
            raise FeedConflict()

        if self.url and self.directory:
            mess = """\
Bad configuration for package %s. 'directory' and 'url' are
mutually exclusive
"""
            raise qisys.error.Error(mess % self.name)

        qibuild.deps.read_deps_from_xml(self, element)

    def _set_property(self, package_xml, name, element):
        """ Helper for load_package_xml

        This makes sure that:

         * no property is overwritten by an None value
         * package.xml is consistent with the feed

        Return True if in the case, and False otherwise
        """
        res = True
        to_set = element.get(name)
        # Never override existing property by a None value
        if to_set:
            orig_property = getattr(self, name)
            if orig_property and orig_property != to_set:
                res = False
                _on_bad_package_xml(package_xml, name, orig_property, to_set)
            setattr(self, name, to_set)
        return res

    def write_package_xml(self):
        """ Dump metadata in self.path/package.xml
        Mainly useful for tests

        """
        package_xml = os.path.join(self.path, "package.xml")
        package_elem = self.to_xml()
        qisys.qixml.write(package_elem, package_xml)

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
    res = QiPackage(None) # need to pass an argument to the ctor
    name = element.get("name")
    if not name:
        raise qisys.error.Error("missing 'name' attribute")
    url = element.get("url")
    if element.tag == "svn_package":
        import qitoolchain.svn_package
        res = qitoolchain.svn_package.SvnPackage(None)
    res.load_package_xml(element=element)
    return res

def from_archive(archive_path):
    archive = zipfile.ZipFile(archive_path)
    try:
        xml_data = archive.read("package.xml")
    except KeyError:
        raise qisys.error.Error("Could not find package.xml in %s" %
                                archive_path)
    element = etree.fromstring(xml_data)
    return from_xml(element)

def extract(archive_path, dest):
    if archive_path.endswith((".tar.gz", ".tbz2")):
       return _extract_legacy(archive_path, dest)
    with zipfile.ZipFile(archive_path) as archive:
        if "package.xml" in archive.namelist():
            return _extract_modern(archive_path, dest)
        else:
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
    else:
        return extract_path

def _on_bad_package_xml(package_xml, name, old, new):
    mess = list()
    if package_xml:
        mess = ["When parsing", package_xml, "\n"]
    mess.extend(["Overriding", name, old, "->", new])
    ui.error(*mess)

class FeedConflict(qisys.error.Error):
    def __str__(self):
        return "Conflict between feed and package.xml"
