#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Check the given pkg satisfy default package requirements to be published """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import zipfile

import qipkg.manifest
import qisys.qixml
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.default_parser(parser)
    parser.add_argument("pkg_path")


def do(args):
    """ Main Entry Point """
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
