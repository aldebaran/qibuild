import os
import zipfile

from qisys.qixml import etree
import qisys.version

class QiPackage(object):
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.path = None
        self.url = None
        self.directory = None
        self.toolchain_file = None
        self.sysroot = None
        self.cross_gdb = None

    def install(self, destdir, runtime=True, release=True):
        mask = list()
        if runtime:
            mask.extend(self._read_install_mask("runtime"))
        if release:
            mask.extend(self._read_install_mask("release"))
        return self._install_with_mask(destdir, mask, release=release)

    def _read_install_mask(self, mask_name):
        mask_path = os.path.join(self.path, mask_name + ".mask")
        if not os.path.exists(mask_path):
            return list()
        with open(mask_path, "r") as fp:
            mask = fp.readlines()
            mask = [x.strip() for x in mask]
            return mask

    def _install_with_mask(self, destdir, mask, release=False):
        if release and not mask:
            filter_fun = qisys.sh.is_runtime
        else:
            def filter_fun(src):
                return "/" + src not in mask
        return qisys.sh.install(self.path, destdir, filter_fun=filter_fun)

    def __repr__(self):
        return "<Package %s %s>" % (self.name, self.version)

    def __str__(self):
        if self.version:
            res = "%s-%s" % (self.name, self.version)
        else:
            res = self.name
        if self.path:
            res += "in %s" % self.path
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
    version = element.get("version")
    res = QiPackage(name, version)
    res.path = element.get("path")
    res.url = element.get("url")
    res.directory = element.get("directory")
    res.toolchain_file = element.get("toolchain_file")
    res.sysroot = element.get("sysroot")
    res.cross_gdb = element.get("cross_gdb")
    return res

def from_archive(archive_path):
    archive = zipfile.ZipFile(archive_path)
    xml_data = archive.read("package.xml")
    element = etree.fromstring(xml_data)
    return from_xml(element)
