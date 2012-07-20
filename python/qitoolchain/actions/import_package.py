## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Import a binary package into a toolchain.
"""

import os
import subprocess

import qibuild
import qitoolchain
import qitoolchain.binary_package

_CMAKE_MODULE_PKG_LIST = """
Package {0} already provides the following CMake module(s):
{1}
You can find it/them at the above location(s) from the package installation
directory (run 'qitoolchain info' to get it).
"""

_CMAKE_MODULE_QIBUILD_LIST = """
qiBuild already provides the following CMake module(s) for the package {0}:
{1}
"""

_MESSAGE_START = "Importing '{1}' in the toolchain '{0}' ..."

_MESSAGE_END = "Package '{1}' has successfully been added to the toolchain '{0}'."

def _fix_pkgtree(root_dir):
    """ Make the package tree comply with qiBuild.

    """
    for item in os.listdir(os.path.join(root_dir, 'usr')):
        src = os.path.join(root_dir, 'usr', item)
        dst = os.path.join(root_dir, item)
        if os.path.exists(dst):
            mess = "Destination already exists"
            raise Exception(mess)
        qibuild.sh.mv(src, dst)
    qibuild.sh.rm(os.path.join(root_dir, 'usr'))
    return

def _convert_to_qibuild(qipkg_dir, package, package_names):
    """ Convert a binary package into a qiBuild package.

    :return: path to the qiBuild package

    """
    with qibuild.sh.TempDir() as work_dir:
        root_dir = package.extract(work_dir)
        _checks = _check_for_cmake_module(root_dir, package_names)
        cmake_found, from_pkg, from_qibuild = _checks
        prefix_ = os.path.join(work_dir, 'usr') + os.sep
        if cmake_found:
            if len(from_pkg) > 0:
                list_ = [ x.replace(prefix_, '') for x in from_pkg ]
                list_ = ''.join([ '  {0}\n'.format(x) for x in list_ ])
                print _CMAKE_MODULE_PKG_LIST.format(package_names[0], list_)
            if len(from_qibuild) > 0:
                list_ = ''.join([ '  {0}\n'.format(x) for x in from_pkg ])
                print _CMAKE_MODULE_QIBUILD_LIST.format(package_names[0], list_)
        else:
            _generate_cmake_module(root_dir, package_names)

        _fix_pkgtree(root_dir)
        qipkg_path = qibuild.archive.zip(root_dir)
        qipkg_file = os.path.basename(qipkg_path)
        qibuild.sh.mv(qipkg_path, qipkg_dir)
        qipkg_path = os.path.join(qipkg_dir, qipkg_file)
        qipkg_path = os.path.abspath(qipkg_path)
    return qipkg_path


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("package_name", metavar='NAME',
        help="The name of the package", nargs='?')
    parser.add_argument("package_path", metavar='PATH',
        help="The path to the package")
    return

def do(args):
    """ Import a binary package into a toolchain

    - Check that there is a CMake module into the binary package
    - Add the qiBuild package to the cache
    - Add the qiBuild package from cache to toolchain

    """
    tc_name = qitoolchain.toolchain_name_from_args(args)
    tc = qitoolchain.get_toolchain(tc_name)

    package_name = args.package_name
    package_path = args.package_path

    with qibuild.sh.TempDir() as tmp:
        package = qitoolchain.binary_package.open_package(package_path)

    package_metadata = package.get_metadata()

    if package_name is None:
        package_name = package_metadata['name']

    package_names = [ package_name, package_metadata['name'] ]
    package_names = list(set(package_names))

    # extract it to the default packages path of the toolchain
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc.name)
    dest = os.path.join(tc_packages_path, package_name)
    qibuild.sh.rm(dest)
    qibuild.ui.info(_MESSAGE_START.format(tc.name, package_name))
    with qibuild.sh.TempDir() as tmp:
        qibuild_pkg = _convert_to_qibuild(tmp, package, package_names)
        extracted = qibuild.archive.extract(qibuild_pkg, tmp, quiet=True)
        qibuild.sh.install(extracted, dest, quiet=True)
    qibuild_package = qitoolchain.Package(package_name, dest)
    tc.add_package(qibuild_package)
    qibuild.ui.info(_MESSAGE_END.format(tc.name, package_name))
