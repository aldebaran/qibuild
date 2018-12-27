# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Extract the contents of a package """

import os
import zipfile

import qipkg.builder
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.default_parser(parser)
    parser.add_argument("pkg_path")
    parser.add_argument("--cwd", "-C", dest="output_path")


def do(args):
    """ Main Entry Point """
    pkg_path = args.pkg_path
    output_path = args.output_path
    if not output_path:
        output_path = os.getcwd()
    # Extract the manifest to a tempfile to parse it
    archive = zipfile.ZipFile(pkg_path)
    pkg_name = None
    with qisys.sh.TempDir() as tmp:
        for name in archive.namelist():
            if name == "manifest.xml":
                archive.extract("manifest.xml", path=tmp)
                manifest_xml_path = os.path.join(tmp, "manifest.xml")
                pkg_name = qipkg.builder.pkg_name(manifest_xml_path)
                break
    if pkg_name is not None:
        to_make = os.path.join(output_path, os.path.basename(pkg_name))
        output_path = os.path.join(output_path, pkg_name)
        qisys.sh.mkdir(to_make, recursive=True)
    archive.close()
    if pkg_path.endswith(".mpkg"):
        basename = os.path.basename(pkg_path)
        name, _ = os.path.splitext(basename)
        output_path = os.path.join(output_path, name)
    qisys.archive.extract(pkg_path, output_path, algo="zip", strict_mode=False)
    ui.info(ui.green, "Package extracted to", ui.reset,
            ui.bold, output_path)
