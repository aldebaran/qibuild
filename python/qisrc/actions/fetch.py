## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
import urllib
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
    toc_cfg = toc.config_path
    toc_configstore = qibuild.configstore.ConfigStore()
    toc_configstore.read(toc_cfg)
    if args.url:
       manifest_url = args.url
    else:
        manifest_url = toc_configstore.get("manifest.url")
        if manifest_url is None:
            mess  = "Could not find URL fo fetch from.\n"
            mess += "Here is what you can do:\n"
            mess += " - specify an URL from the command line\n"
            mess += " - edit %s to have: \n\n" % toc_cfg
            mess += """[manifest]
url = ftp://example.com/foo.manifest
"""
            raise Exception(mess)

    qiwt = qibuild.worktree_open(args.work_tree)

    projects = qisrc.parse_manifest(manifest_url)
    for (project_name, project_url) in projects.iteritems():
        if project_name in qiwt.git_projects.keys():
            LOGGER.info("Found %s, skipping", project_name)
        else:
            qibuild.run_action("qisrc.actions.add", [project_url, project_name])

    # Everything went fine, store the manifest URL for later use:
    qibuild.configstore.update_config(toc_cfg, "manifest", "url", manifest_url)


