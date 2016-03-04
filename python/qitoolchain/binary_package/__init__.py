## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module contains function to import binary packages in qiBuild
toolchains.

qiBuild toolchains contain a set of packages which can be extended.

This module provides utility functions to import binary packages used by some
other compatible distribution into a qiBuild toolchain.

All qiBuild packages should have the same layout.
"""

import os

import qisys
import qisys.sh
import qisys.ui
from qisys.qixml import etree
from qitoolchain.binary_package.core import BinaryPackage
from qitoolchain.binary_package.core import BinaryPackageException

WITH_PORTAGE = True
try:
    #pylint: disable-msg=F0401
    import portage
except ImportError:
    WITH_PORTAGE = False

if WITH_PORTAGE:
    from qitoolchain.binary_package.gentoo_portage import GentooPackage
else:
    from qitoolchain.binary_package.gentoo import GentooPackage

_PKG_TYPES = {
    'gentoo': {
        'extension': '.tbz2',
        'class': GentooPackage,
    },
    # Not yet implemented, so use the default Package class
    'debian': {
        'extension': '.deb',
        'class': BinaryPackage,
    },
    'redhat': {
        'extension': '.rpm',
        'class': BinaryPackage,
    },
    'archlinux': {
        'extension': '.pkg.tar.xz',
        'class': BinaryPackage,
    },
}


def _guess_package_type(package_path):
    for typename, data in _PKG_TYPES.iteritems():
        if package_path.endswith(data.get('extension')):
            return  typename
    return None


def open_package(package_path):
    """ Open the given binary package.

    :return: A ``Package`` instance

    """
    if not os.path.exists(package_path):
        mess = "No such file or directory: {0}".format(package_path)
        raise SystemError(mess)
    package = None
    typename = _guess_package_type(package_path)
    if not typename:
        mess = "Unknown package type"
        raise BinaryPackageException(mess)
    generator = _PKG_TYPES.get(typename).get('class')
    package = generator(package_path)
    return package


def _fix_package_tree(root_dir):
    """ Make the package tree comply with qiBuild.

    """
    # move stuff from usr/lib to lib
    # this is just for qibuild deploy to work,
    # we could do better with cmake.
    usr_dir = os.path.join(root_dir, "usr")
    if not os.path.exists(usr_dir):
        return

    for (root, dirs, files) in os.walk(usr_dir):
       for directory in dirs:
            dst = os.path.join(root, directory)
            dst = dst.replace(usr_dir, root_dir)
            qisys.sh.mkdir(dst)
       for filename in files:
            src = os.path.join(root, filename)
            dst = src.replace(usr_dir, root_dir)
            qisys.sh.mv(src, dst)
    qisys.sh.rm(usr_dir)


def convert_to_qibuild(package, package_metadata=None,
                       output_dir=None, output_name=None):
    """ Convert a binary package into a qiBuild package.

    :param package: an instance of qitoolchain.binary_package.BinaryPackage.
    :param package_metadata: a dict to override the metadata of the package,
                             or to provide the metadata if the could not be
                             read from the binary package
    :param output_dir: where to put the new qiBuild package, defaults to
                       the basename of the binary package
    :package output_name: the archive name of the qiBuild package,
                          computed from the metadata if not given
    :param gen_cmake: whether we should try to generate a CMake module for
                      this package
    :return: path to the converted qiBuild package

    """
    metadata = package.get_metadata()
    if package_metadata:
        metadata.update(package_metadata)
    package_name = metadata["name"]
    if not output_dir:
        output_dir = os.path.dirname(package.path)
    if not output_name:
        output_name = package_name
        for key in ['version', 'revision', 'arch', 'arch_variant']:
            value = metadata.get(key)
            if value:
                if key == 'revision':
                    value = "r" + value
                output_name += "-" + value
        output_name += ".zip"
    qisys.sh.mkdir(output_dir, recursive=True)
    output_path = os.path.join(output_dir, output_name)
    with qisys.sh.TempDir() as work_dir:
        root_dir = package.extract(work_dir)
        _fix_package_tree(root_dir)
        package_xml_path = os.path.join(root_dir, "package.xml")
        package_xml_root = etree.Element("package")
        package_xml_tree = etree.ElementTree(package_xml_root)
        package_xml_root.set("name", package_name)
        version = metadata.get("version")
        if version:
            package_xml_root.set("version", version)
        qisys.qixml.write(package_xml_root, package_xml_path)
        res = qisys.archive.compress(root_dir, algo="zip", quiet=True, flat=True)
        qisys.sh.mv(res, output_path)
    return output_path
