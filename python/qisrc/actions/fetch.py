## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Read a list of projects to clone from a manifest URL

The url should point to a xml file looking like

<manifest>
    <project
        name="foo"
        url="git://foo.com/foo.git"
    />
    <manifest
        url = "http://example.org/an_other_manifest.xml"
    />
<manifest>



"""

import os
import logging

import qisrc
import qibuild

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("url",
        nargs = "?",
        metavar="URL",
        help="URL of the manifest. "
        "If not specified, use the last known url")


def do(args):
    """Main entry point

    """
    print "Use qisrc sync instead"


