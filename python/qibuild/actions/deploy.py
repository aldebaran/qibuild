## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Deploy code to a remote target """

import os

import qibuild
import qibuild.deploy
import qibuild.install


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("url", help="remote url: user@hostname:path")
    parser.add_argument("-p", "--port", help="port", type=int)
    parser.set_defaults(port=22)

def do(args):
    """Main entry point"""
    url = args.url
    (username, several, path) = qibuild.deploy.parse_url(args.url)
    toc = qibuild.toc_open(args.worktree, args)
    rsync = qibuild.command.find_program("rsync", env=toc.build_env)
    use_rsync = False
    if rsync:
        use_rsync = True
    else:
        scp = qibuild.command.find_program("scp", env=toc.build_env)
        if not scp:
            raise Exception("Could not find rsync or scp")

    with qibuild.sh.TempDir() as destdir:
        qibuild.install.install_projects(toc, destdir, runtime=True,
                                         prefix="/",
                                         include_deps=True)
        qibuild.deploy.deploy(destdir, args.url, use_rsync=use_rsync, port=args.port)
