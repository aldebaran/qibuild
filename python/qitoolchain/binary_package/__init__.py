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

import qibuild
import qibuild.cmake.modules as cmake_modules
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
    usr_dir = os.path.join(root_dir, 'usr')
    if not os.path.exists(usr_dir):
        return
    for item in os.listdir(usr_dir):
        src = os.path.join(root_dir, 'usr', item)
        dst = os.path.join(root_dir, item)
        if os.path.exists(dst):
            mess = "Destination already exists"
            raise Exception(mess)
        qibuild.sh.mv(src, dst)
    qibuild.sh.rm(os.path.join(root_dir, 'usr'))
    return


def convert_to_qibuild(dest_dir, package, package_name, other_names=None,
                       package_metadata=None, interactive=True):
    """ Convert a binary package into a qiBuild package.

    :param dest_dir:     destination directory for the converted qiBuild
                         package
    :param package:      input package to be converted, it could be either a
                         path to a directory, or a path to a archive, or an
                         instance of qitoolchain.binary_package.BinaryPackage.
    :param package_name: name of the qiBuild package
    :param other_name:   other names which could match existing CMake modules

    :return: tuple (path to the qiBuild package,
                    list of CMake module found in the package,
                    list of CMake module provided by qiBuild)

    """
    modules_package = list()
    modules_qibuild = list()
    qipkg_path      = None
    pkg_names = list()
    if other_names is not None:
        pkg_names.extend(other_names)
    pkg_names.append(package_name)
    pkg_names = list(set(pkg_names))
    if isinstance(package, BinaryPackage):
        package_type = "binpkg_object"
    elif os.path.exists(package) and os.path.isdir(package):
        package_type = "directory"
    elif os.path.exists(package) and os.path.isdir(package):
        package = open_package(package)
        package_type = "binpkg_object"
    else:
        message = """
unsupported operand type: {0} (type: {1})
""".format(str(package), type(package))
        raise TypeError(message)
    if package_type == "binpkg_object" and not package_metadata:
        package_metadata = package.get_metadata()
    with qibuild.sh.TempDir() as work_dir:
        if package_type == "binpkg_object":
            root_dir = package.extract(work_dir)
        elif package_type == "directory":
            root_dir = os.path.join(work_dir, os.path.basename(package))
            qibuild.sh.install(package, root_dir, quiet=True)
        else:
            message = "Unsupported package type: {0}".format(package_type)
            raise RuntimeError(message)
        top_dir = os.path.basename(root_dir)
        pkg_names.append(top_dir)
        pkg_names = list(set(pkg_names))
        _fix_package_tree(root_dir)
        path_list  = qibuild.sh.ls_r(root_dir)
        checks = cmake_modules.check_for_module_generation(pkg_names,
                                                           path_list=path_list)
        module_status   = checks[0]
        modules_package = checks[1]
        modules_qibuild = checks[2]
        need_generation = module_status == "nonexistent"
        cmake_modules.show_exiting_modules(package_name, modules_package,
                                           modules_qibuild)
        if interactive and module_status == "provided_by_qibuild":
            question = """\
Do you want to generate a CMake module for {0},
though some from qiBuild may already exist for this package?\
""".format(package_name)
            need_generation = qibuild.interact.ask_yes_no(question, default=False)
        cmake_module = cmake_modules.CMakeModule(name=package_name)
        if need_generation:
            cmake_module.generate_from_directory(root_dir, package_name,
                                                 path_list=path_list,
                                                 interactive=interactive)
            cmake_module.write(root_dir)
        qipkg_name = cmake_module.name
        if package_metadata:
            for key in ['version', 'revision', 'arch', 'arch_variant']:
                if key in package_metadata and package_metadata[key]:
                    qipkg_name += "-{0}".format(package_metadata[key])
        if top_dir != qipkg_name:
            src = root_dir
            dst = os.path.join(os.path.dirname(root_dir), qipkg_name)
            qibuild.sh.mv(src, dst)
            root_dir = dst
        qipkg_path = qibuild.archive.compress(root_dir, algo="zip", quiet=True)
        src = qipkg_path
        dst = os.path.join(dest_dir, os.path.basename(qipkg_path))
        qibuild.sh.rm(dst)
        qibuild.sh.mv(src, dst)
        qipkg_path = os.path.abspath(dst)
    return (qipkg_path, modules_package, modules_qibuild)
