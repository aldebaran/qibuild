## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Deploy code to a remote target """

import os

import qibuild
import qibuild.deploy


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
    (username, server, remote_directory) = qibuild.deploy.parse_url(url)
    toc = qibuild.toc_open(args.worktree, args)
    rsync = qibuild.command.find_program("rsync", env=toc.build_env)
    use_rsync = False
    if rsync:
        use_rsync = True
    else:
        scp = qibuild.command.find_program("scp", env=toc.build_env)
        if not scp:
            raise Exception("Could not find rsync or scp")

    config = toc.active_config
    if not config:
        config = "system"
    destdir = os.path.join("~/.local/share/qi", "deploy", config, remote_directory)
    destdir = qibuild.sh.to_native_path(destdir)

    # Resolve deps:
    (project_names, package_names, _) = toc.resolve_deps(runtime=True)

    # Install packages to destdir:
    if not args.single:
        for package_name in package_names:
            toc.toolchain.install_package(package_name, destdir, runtime=True)

    # Install projects to destdir:
    for project_name in project_names:
        project = toc.get_project(project_name)
        toc.install_project(project, destdir, prefix="/",
                            runtime=True, num_jobs=args.num_jobs)


    qibuild.deploy.deploy(destdir, args.url, use_rsync=use_rsync, port=args.port)
