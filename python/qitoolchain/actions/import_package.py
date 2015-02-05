## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Convert a binary archive into a qiBuild package and add it to a toolchain.

"""

import os

from qisys import ui
import qisys.parsers
import qitoolchain
import qitoolchain.parsers
from qitoolchain.convert import convert_package
import qitoolchain.qipackage


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qitoolchain.parsers.toolchain_parser(parser)
    parser.add_argument("--name", required=True,
                        help="The name of the package")
    parser.add_argument("package_path", metavar='PACKAGE_PATH',
                        help="The path to the package to be converted")
    parser.add_argument("-d", "--directory", dest="dest_dir",
                        metavar='DESTDIR', help="""\
destination directory of the qiBuild package after conversion
(default: aside the original package)""")
    parser.add_argument("--batch", dest="interactive", action="store_false",
                        help="Do not prompt for cmake module edition")
    parser.set_defaults(interactive=True)


def do(args):
    """ Import a binary package into a toolchain

    - Convert the binary package into a qiBuild package
    - Add the qiBuild package to the cache
    - Add the qiBuild package from cache to toolchain

    """
    name = args.name
    package_path = args.package_path
    converted_package_path = convert_package(package_path, name,
                                             interactive=args.interactive)
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
        extracted = qisys.archive.extract(converted_package_path, tmp, quiet=True,
                                          strict_mode=False)
        qisys.sh.install(extracted, package_dest, quiet=True)
    qibuild_package = qitoolchain.qipackage.QiPackage(name, path=package_dest)
    toolchain.add_package(qibuild_package)
    ui.info("done")
