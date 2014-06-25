## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Convert a binary archive into a qiBuild package and add it to a toolchain.

"""

import os

from qisys import ui
import qisys
import qitoolchain
from qitoolchain.convert import convert_package


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("-c", "--config",
                        help="name of the toolchain to use")
    parser.add_argument("--name", required=True,
                        help="The name of the package")
    parser.add_argument("package_path", metavar='PACKAGE_PATH',
                        help="""\
The path to the package (archive  or root install directory) to be convert.
If PACKAGE_PATH points to a directory, then NAME is a mandatory.""")
    parser.add_argument("-d", "--directory", dest="dest_dir",
                        metavar='DESTDIR', help="""\
destination directory of the qiBuild package after convertsion
(default: aside the original package)""")
    return


def do(args):
    """ Import a binary package into a toolchain

    - Convert the binary package into a qiBuild package
    - Add the qiBuild package to the cache
    - Add the qiBuild package from cache to toolchain

    """
    name = args.name
    package_path = args.package_path
    converted_package_path = convert_package(package_path, name, interactive=True)
    toolchain = qitoolchain.parsers.get_toolchain(args)
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(toolchain.name)
    message = """
Importing '{1}' in the toolchain {0} ...
""".format(toolchain.name, package_path)
    qisys.ui.info(message)
    # installation of the qiBuild package
    package_dest = os.path.join(tc_packages_path, name)
    qisys.sh.rm(package_dest)
    with qisys.sh.TempDir() as tmp:
        extracted = qisys.archive.extract(converted_package_path, tmp, quiet=True)
        qisys.sh.install(extracted, package_dest, quiet=True)
    qibuild_package = qitoolchain.Package(name, package_dest)
    toolchain.add_package(qibuild_package)
    ui.info("done")
