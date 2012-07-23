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
