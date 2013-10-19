## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Deploy package using Maven.
"""

import sys
import os

import qibuild.find
import qibuild.parsers
from qisys import ui
from qimvn import deploy

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.build_parser(parser)
    parser.add_argument("package")
    parser.add_argument("--artifactId", required=True, dest="artifact_id", help="name")
    parser.add_argument("--url", required=True, dest="url", help="destination url")
    parser.add_argument("--groupId", required=True, dest="group_id", help="group name (i.e: 'com.aldebaran')")
    parser.add_argument("--version", default="1.0-SNAPSHOT", dest="version", help="version (default: '1.0-SNAPSHOT)")
    parser.add_argument("--packaging", default="jar", dest="packaging", help="packaging type {jar, apklib} (default: 'jar')")

def do(args):
    """Main entry point """
    return deploy.deploy(args.group_id, args.version, args.artifact_id,
                         args.package, args.url, args.packaging)
