## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Import a package (binary archive or install directory) into a qiBuild package
and add it to a toolchain.

"""

import os
import subprocess

import qibuild
import qitoolchain
from qitoolchain.binary_package import open_package
from qitoolchain.binary_package import convert_to_qibuild


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("package_name", metavar='NAME',
                        help="The name of the package", nargs='?')
    parser.add_argument("package_path", metavar='PACKAGE_PATH',
                        help="""\
The path to the package (archive  or root install directory) to be convert.
If PACKAGE_PATH points to a directory, then NAME is a mandatory.""")
    parser.add_argument("-d", "--directory", dest="dest_dir",
                        metavar='DESTDIR', help="""\
destination directory of the qiBuild package after convertsion
(default: aside the original package)""")
    parser.add_argument("-b", "--batch", dest="batch", action="store_true",
                        default=False, help="enable non-interactive mode")
    return


def do(args):
    """ Import a binary package into a toolchain

    - Convert the binary package into a qiBuild package
    - Add the qiBuild package to the cache
    - Add the qiBuild package from cache to toolchain

    """
    tc_name = qitoolchain.toolchain_name_from_args(args)
    tc = qitoolchain.get_toolchain(tc_name)

    package_name = args.package_name
    package_path = os.path.abspath(args.package_path)
    dest_dir     = args.dest_dir
    interactive  = not args.batch
    other_names  = list()
    if dest_dir is None:
        dest_dir = os.path.dirname(package_path)
    if os.path.isdir(package_path):
        if package_name is None:
            message = """
Error: when turning an install directory into a qiBuild package,
a package name must be passed to the command line.
"""
            raise Exception(message)
        package = package_path
    else:
        package = open_package(package_path)
        package_metadata = package.get_metadata()
        if package_name is None:
            package_name = package_metadata['name']
            other_names.append(package_metadata['name'])
    other_names.append(package_name)
    other_names = list(set(other_names))
    # extract it to the default packages path of the toolchain
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc.name)
    package_dest = os.path.join(tc_packages_path, package_name)
    qibuild.sh.rm(package_dest)
    message = """
Importing '{1}' in the toolchain {0} ...
""".format(tc.name, package_path)
    qibuild.ui.info(message)
    # conversion into qiBuild
    with qibuild.sh.TempDir() as tmp:
        conversion = convert_to_qibuild(tmp, package, package_name,
                                        other_names=other_names,
                                        interactive=interactive)
        qibuild_package_path = conversion[0]
        modules_package      = conversion[1]
        modules_qibuild      = conversion[2]
        src = os.path.abspath(qibuild_package_path)
        dst = os.path.join(dest_dir, os.path.basename(qibuild_package_path))
        dst = os.path.abspath(dst)
        qibuild.sh.mkdir(dest_dir, recursive=True)
        qibuild.sh.rm(dst)
        qibuild.sh.mv(src, dst)
        qibuild_package_path = dst
    # installation of the qiBuild package
    with qibuild.sh.TempDir() as tmp:
        extracted = qibuild.archive.extract(qibuild_package_path, tmp, quiet=True)
        qibuild.sh.install(extracted, package_dest, quiet=True)
    qibuild_package = qitoolchain.Package(package_name, package_dest)
    tc.add_package(qibuild_package)
    # end :)
    package_content = qibuild.sh.ls_r(package_dest)
    modules_list = qibuild.cmake.modules.find_cmake_module_in(package_content)
    modules_list = [os.path.join(package_dest, cmake_) for cmake_ in modules_list]
    modules_list.extend(modules_qibuild)
    modules_list = ["  {0}".format(module_) for module_ in modules_list]
    modules_list = "\n".join(modules_list)
    message = """\
Import succedded.

qiBuild package:
  {2}

Package '{1}' has been added to the toolchain '{0}'.

To use this package in your project, you may want to check out:
{3}
""".format(tc.name, package_name, qibuild_package_path, modules_list)
    qibuild.ui.info(message)
