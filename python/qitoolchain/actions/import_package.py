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

    package_names = [ package_metadata['name'] ]
    if not package_name in package_names:
        package_names.insert(0, package_name)

    # extract it to the default packages path of the toolchain
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc.name)
    dest = os.path.join(tc_packages_path, package_name)
    qibuild.sh.rm(dest)
    qibuild.ui.info(_MESSAGE_START.format(tc.name, package_name))
    with qibuild.sh.TempDir() as tmp:
        conversion  = qitoolchain.binary_package.convert_to_qibuild(tmp, package, package_names)
        qibuild_pkg = conversion[0]
        modules_from_pkg     = conversion[1]
        modules_from_qibuild = conversion[2]
        if len(modules_from_pkg) > 0:
            list_ = "".join(["  {0}\n".format(x) for x in modules_from_pkg])
            print _CMAKE_MODULE_PKG_LIST.format(package_name, list_)
        if len(modules_from_qibuild) > 0:
            list_ = "".join(["  {0}\n".format(x) for x in modules_from_qibuild])
            print _CMAKE_MODULE_PKG_LIST.format(package_name, list_)
        extracted   = qibuild.archive.extract(qibuild_pkg, tmp, quiet=True)
        qibuild.sh.install(extracted, dest, quiet=True)
    qibuild_package = qitoolchain.Package(package_name, dest)
    tc.add_package(qibuild_package)
    qibuild.ui.info(_MESSAGE_END.format(tc.name, package_name))
