## Copyright (C) 2011 Aldebaran Robotics

""" Read a list of projects to clone from a manifest URL

The url should point to a file looking like

[project "foo"]
url = git://foo.com/foo.git


"""

import os
import urllib
import logging

import qibuild

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.qiworktree.work_tree_parser(parser)
    parser.add_argument("url",
        nargs = "?",
        metavar="URL",
        help="URL of the manifest. "
        "If not specified, use the last known url")


def do(args):
    """Main entry point

    """
    qiwt = qibuild.qiworktree_open(args.work_tree)
    qibuild_cfg = os.path.join(qiwt.work_tree, ".qi", "qibuild.cfg")
    qibuild_store = qibuild.configstore.ConfigStore()
    qibuild_store.read(qibuild_cfg)
    if args.url:
       manifest_url = args.url
    else:
        # Read it from conf:
        manifest_url = qibuild_store.get("manifest", "url")
        if manifest_url is None:
            mess  = "Could not find URL fo fetch from.\n"
            mess += "Here is what you can do:\n"
            mess += " - specify an URL from the command line\n"
            mess += " - edit %s to have: \n\n" % qibuild_cfg
            mess += """[manifest]
url = ftp://example.com/foo.manifest
"""
            raise Exception(mess)

    config = qibuild.configstore.ConfigStore()
    with qibuild.sh.TempDir() as tmp:
        manifest = os.path.join(tmp, "manifest")
        urllib.urlretrieve(args.url, manifest)
        config.read(manifest)

    projects = config.get("project", default=None)
    if not projects:
        raise Exception("Not project found in url %s" % args.url)

    qiwt = qibuild.qiworktree_open(args.work_tree)

    for (project_name, project_conf) in config.get("project").iteritems():
        project_url = config.get("project", project_name, "url")
        if project_name in qiwt.buildable_projects.keys():
            LOGGER.info("Found %s, skipping", project_name)
        else:
            try:
                qibuild.run_action("qisrc.actions.add", [project_url, project_name])
            except qibuild.qiworktree.ProjectAlreadyExists:
                pass

    # Everything went fine, store the manifest URL for later use:
    qibuild.configstore.update_config(qibuild_cfg, "manifest", "url", manifest_url)


