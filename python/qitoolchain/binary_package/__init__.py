## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
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
from qitoolchain.binary_package.core import BinaryPackage
from qitoolchain.binary_package.core import BinaryPackageException

WITH_PORTAGE = True
try:
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
    if typename is None:
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
    usr_lib = os.path.join(root_dir, "usr/lib")
    if not os.path.exists(usr_lib):
        return
    lib_dir = os.path.join(root_dir, "lib")
    qisys.sh.mkdir(lib_dir)

    for (root, directories, filenames) in os.walk(usr_lib):
        for filename in filenames:
            src = os.path.join(root, filename)
            print "mv", src, "->", lib_dir
            qisys.sh.mv(src, lib_dir)


def convert_to_qibuild(package, package_metadata=None,
                       output_dir=None, output_name=None):
    """ Convert a binary package into a qiBuild package.

    :param package: an instance of qitoolchain.binary_package.BinaryPackage.
    :param package_metadata: a dict to override the metadata of the package,
                             or to provide the metadata if the could not be
                             read from the binary package
    :param output_dir: where to put the new qiBuild package, defaults to
                       the basename of the binaray package
    :package output_name: the archive name of the qiBuild package,
                          computed from the metadat if not given
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
                output_name += "-" + value
        output_name += ".zip"
    qisys.sh.mkdir(output_dir, recursive=True)
    output_path = os.path.join(output_dir, output_name)
    with qisys.sh.TempDir() as work_dir:
        root_dir = package.extract(work_dir)
        _fix_package_tree(root_dir)
        res = qisys.archive.compress(root_dir, algo="zip", quiet=True)
        qisys.sh.mv(res, output_path)
    return output_path
