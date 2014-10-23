import os
import re
import zipfile

from qisys.qixml import etree
import qisys.version
import qibuild.deps

class QiPackage(object):
    """ Binary package for use with qibuild.

    Package names are unique in a given toolchain.
    path is None until the package is added to a database

    """
    def __init__(self, name, version=None, path=None):
        self.name = name
        self.version = version
        self.path = path
        self.url = None
        self.directory = None
        self.toolchain_file = None
        self.sysroot = None
        self.cross_gdb = None
        self.build_depends = set()
        self.run_depends = set()
        self.test_depends = set()

    def load_deps(self):
        """ Parse package.xml, set the dependencies """
        package_xml = os.path.join(self.path, "package.xml")
        if os.path.exists(package_xml):
            xml_root = qisys.qixml.read(package_xml)
            qibuild.deps.read_deps_from_xml(self, xml_root)

    def install(self, destdir, components=None, release=True):
        """ Install the given components of the package to the given destination

        Will read

        * ``install_manifest_<component>.txt`` for each component if the file exists
        * ``<component>.mask`` to exclude files matching some regex if the mask exists
        * if none exits, will apply the ``qisys.sh.is_runtime`` filter when
          installing *runtime* component

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
        return qisys.sh.install(self.path, destdir)

    def _install_component(self, component, destdir, release=True):
        installed_files = list()
        manifest_name = "install_manifest_%s.txt" % component
        if not release:
            manifest_name = "install_manifest_%s_debug.txt" % component
        manifest_path = os.path.join(self.path, manifest_name)
        if not os.path.exists(manifest_path):
            mask = self._read_install_mask(component)
            if release:
                mask.extend(self._read_install_mask("release"))
            if not mask and component=="runtime":
                # retro-compat
                return qisys.sh.install(self.path, destdir,
                                        filter_fun=qisys.sh.is_runtime)
            else:
                # avoid install masks and package.xml
                mask.append(".*\.mask")
                mask.append("package\.xml")
                return self._install_with_mask(destdir, mask)
        else:
            with open(manifest_path, "r") as fp:
                lines = fp.readlines()
                for line in lines:
                    line = line.strip()
                    line = line[1:] # remove leading "/"
                    src = os.path.join(self.path, line)
                    dest = os.path.join(destdir, line)
                    qisys.sh.install(src, dest)
                    installed_files.append(dest)
            return installed_files


    def _read_install_mask(self, mask_name):
        mask_path = os.path.join(self.path, mask_name + ".mask")
        if not os.path.exists(mask_path):
            return list()
        with open(mask_path, "r") as fp:
            mask = fp.readlines()
            mask = [x.strip() for x in mask]
            return mask

    def _install_with_mask(self, destdir, mask):
        def filter_fun(src):
            src = qisys.sh.to_posix_path(src)
            src = "/" + src
            for regex in mask:
                match = re.match(regex, src)
                if match:
                    return False
            return True

        return qisys.sh.install(self.path, destdir, filter_fun=filter_fun)

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
    res.toolchain_file = element.get("toolchain_file")
    res.sysroot = element.get("sysroot")
    res.cross_gdb = element.get("cross_gdb")
    qibuild.deps.read_deps_from_xml(res, element)
    return res

def from_archive(archive_path):
    archive = zipfile.ZipFile(archive_path)
    xml_data = archive.read("package.xml")
    element = etree.fromstring(xml_data)
    return from_xml(element)

def extract(archive_path, dest):
    if archive_path.endswith(".tar.gz"):
        _extract_legacy(archive_path, dest)
        return
    with zipfile.ZipFile(archive_path) as archive:
        if "package.xml" in archive.namelist():
            _extract_modern(archive_path, dest)
        else:
            _extract_legacy(archive_path, dest)

def _extract_modern(archive_path, dest):
    qisys.archive.extract(archive_path, dest, strict_mode=False)

def _extract_legacy(archive_path, dest):
    algo = qisys.archive.guess_algo(archive_path)
    extract_dest = os.path.dirname(dest)
    extract_path = qisys.archive.extract(archive_path, extract_dest, algo=algo)
    extract_path = os.path.abspath(extract_path)
    if extract_path != dest:
        qisys.sh.mkdir(dest, recursive=True)
        qisys.sh.rm(dest)
        qisys.sh.mv(extract_path, dest)
        qisys.sh.rm(extract_path)
