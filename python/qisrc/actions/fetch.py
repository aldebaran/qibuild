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
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("url",
        nargs = "?",
        metavar="URL",
        help="URL of the manifest. "
        "If not specified, use the last known url")


def do(args):
    """Main entry point

    """
    toc = qibuild.toc.toc_open(args.work_tree)
    if args.url:
        manifest_url = args.url
    else:
        manifest = toc.config.local.manifest
        if manifest is None:
            mess  = "Could not find URL fo fetch from.\n"
            mess += "Here is what you can do:\n"
            mess += " - specify an URL from the command line\n"
            mess += " - edit %s to have: \n\n" % toc.config_path
            mess += """<qibuild>
            <manifest
                url = ftp://example.com/foo.manifest
            />
</qibuild>
"""
            raise Exception(mess)
        manifest_url = manifest.url

    qiwt = qibuild.worktree_open(args.work_tree)

    projects = qisrc.parse_manifest(manifest_url)
    for (project_name, project_url) in projects.iteritems():
        if project_name not in qiwt.git_projects.keys():
            qibuild.run_action("qisrc.actions.add", [project_url, project_name])
        else:
            p_path = qiwt.git_projects[project_name]
            LOGGER.info("Found project %s, skipping", project_name)

    # Everything went fine, store the manifest URL for later use:
    toc.config.set_manifest_url(manifest_url)
    toc.save_config()


