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
    parser.add_argument("url",  metavar="URL", help="url of the manifest")


def do(args):
    """Main entry point

    """
    config = qibuild.configstore.ConfigStore()
    with qibuild.sh.TempDir() as tmp:
        manifest = os.path.join(tmp, "manifest")
        urllib.urlretrieve(args.url, manifest)
        config.read(manifest)

    projects = config.get("project", default=None)
    if not projects:
        raise Exception("Not project found in url %s" % args.url)

    qiwt = qibuild.qiworktree_open(args.work_tree, use_env=True)

    for (project_name, project_conf) in config.get("project").iteritems():
        project_url = config.get("project", project_name, "url")
        if project_name in qiwt.buildable_projects.keys():
            LOGGER.info("Found %s, skipping", project_name)
        else:
            try:
                qibuild.run_action("qisrc.actions.add", [project_url, project_name])
            except qibuild.qiworktree.ProjectAlreadyExists:
                pass

