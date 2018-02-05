# Copyright (c) 2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Check the given pkg satisfy default package requirements to be published """

import zipfile
import os

from qisys import ui
import qisys.parsers
import qisys.qixml
import qipkg.manifest


def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    parser.add_argument("pkg_path")


def do(args):
    pkg_path = args.pkg_path
    with qisys.sh.TempDir() as tmp:
        archive = zipfile.ZipFile(pkg_path)
        archive.extract("manifest.xml", path=tmp)
        archive.close()

        # read the manifest and validate it
        manifest_path = os.path.join(tmp, "manifest.xml")
        validator = qipkg.manifest.Validator(manifest_path)
        validator.print_errors()
        validator.print_warnings()
        if validator.is_valid:
            ui.info(ui.green, "The package satisfies "
                              "default package requirements")
        else:
            raise Exception("Given package does not satisfy "
                            "default package requirements")
