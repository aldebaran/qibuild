## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Convert a package (binary archive or install directory) into a qiBuild package.

"""

import os

import qibuild
from qitoolchain.binary_package import open_package
from qitoolchain.binary_package import convert_to_qibuild
from qibuild.cmake.modules import add_cmake_module_to_archive

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
                        metavar='DESTDIR',
                        help="qiBuild package destination directory \
                              (default: aside the original package)")
    return


def do(args):
    """Convert a package (binary archive or install directory) into a
    qiBuild package.

    - Check that there is a CMake module for this binary package
      (provided by the package itself or qiBuild)
    - If not CMake module for the package, then generate it
    - Turn the file tree into a qiBuild package
    - Build a qiBuild package

    """
    package_name = args.package_name
    package_path = os.path.abspath(args.package_path)
    dest_dir     = args.dest_dir
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
    message = """
Converting '{0}' into a qiBuild package ...
""".format(package_path)
    qibuild.ui.info(message)

    with qibuild.sh.TempDir() as tmp:
        qibuild_package_path = convert_to_qibuild(package, output_dir=tmp)
        add_cmake_module_to_archive(qibuild_package_path, package.name)
        src = os.path.abspath(qibuild_package_path)
        dst = os.path.join(dest_dir, os.path.basename(qibuild_package_path))
        dst = os.path.abspath(dst)
        qibuild.sh.mkdir(dest_dir, recursive=True)
        qibuild.sh.rm(dst)
        qibuild.sh.mv(src, dst)
        qibuild_package_path = dst
    message = """\
Conversion succedded.

qiBuild package:
  {1}

You can add this qiBuild package to a toolchain using:
  qitoolchain -c <toolchain name> {0} {1}\
""".format(package_name, qibuild_package_path)
    qibuild.ui.info(message)
