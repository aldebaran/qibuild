#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Bump the version number of a given package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qipkg.manifest


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("manifest_xml")
    parser.add_argument("version", nargs="?")


def do(args):
    """ Main entry point """
    manifest_xml_path = args.manifest_xml
    version = args.version
    qipkg.manifest.bump_version(manifest_xml_path, version=version)
