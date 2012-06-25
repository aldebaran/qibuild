## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Deploy code to a remote target """

import os
import logging

import qibuild
import qibuild.sh
import qibuild.deploy

LOGGER = logging.getLogger()

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
        LOGGER.warning("Please install rsync to get faster synchronisation")
        scp = qibuild.command.find_program("scp", env=toc.build_env)
        if not scp:
            raise Exception("Could not find rsync or scp")

    # Resolve deps:
    (project_names, package_names, _) = toc.resolve_deps(runtime=True)

    # Deploy packages: install all of them in the same temp dir, they
    # deploy this temp dir to the target
    if not args.single:
        with qibuild.sh.TempDir() as tmp:
            for package_name in package_names:
                toc.toolchain.install_package(package_name, tmp, runtime=True)
            qibuild.deploy.deploy(tmp, args.url, use_rsync=use_rsync, port=args.port)

    # Deploy projects: install them inside a 'deploy' dir inside the build dir,
    # then deploy this dir to the target
    for project_name in project_names:
        project = toc.get_project(project_name)
        destdir = os.path.join(project.build_directory, "deploy")
        project = toc.get_project(project_name)
        #create folder for project without install rules
        qibuild.sh.mkdir(destdir, recursive=True)
        toc.install_project(project, destdir, prefix="/",
                            runtime=True, num_jobs=args.num_jobs,
                            split_debug=True)
        qibuild.deploy.deploy(destdir, args.url, use_rsync=use_rsync, port=args.port)
        qibuild.deploy.generate_debug_scripts(toc, project_name, args.url)
