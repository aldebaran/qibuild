## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Deploy code to a remote target """

import os

from qibuild import ui
import qibuild
import qibuild.sh
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
    ui.info(ui.green, "Current worktree:", ui.reset, ui.bold, toc.worktree.root)
    if toc.active_config:
        ui.info(ui.green, "Active configuration: ",
                ui.blue, "%s (%s)" % (toc.active_config, toc.build_type))
    rsync = qibuild.command.find_program("rsync", env=toc.build_env)
    use_rsync = False
    if rsync:
        use_rsync = True
    else:
        ui.warning("Please install rsync to get faster synchronisation")
        scp = qibuild.command.find_program("scp", env=toc.build_env)
        if not scp:
            raise Exception("Could not find rsync or scp")

    # Resolve deps:
    (project_names, package_names, _) = toc.resolve_deps(runtime=True)
    projects = [toc.get_project(name) for name in project_names]

    if not args.single:
        ui.info(ui.green, "The following projects")
        for project_name in project_names:
            ui.info(ui.green, " *", ui.blue, project_name)
        if not args.single and package_names:
            ui.info(ui.green, "and the following packages")
            for package_name in package_names:
                ui.info(" *", ui.blue, package_name)
        ui.info(ui.green, "will be deployed to", ui.blue, url)

    # Deploy packages: install all of them in the same temp dir, then
    # deploy this temp dir to the target
    if not args.single and package_names:
        print
        ui.info(ui.green, ":: ", "Deploying packages")
        with qibuild.sh.TempDir() as tmp:
            for (i, package_name) in enumerate(package_names):
                ui.info(ui.green, "*", ui.reset,
                        "(%i/%i)" % (i+1, len(package_names)),
                        ui.green, "Deploying package", ui.blue, package_name,
                        ui.green, "to", ui.blue, url)
                toc.toolchain.install_package(package_name, tmp, runtime=True)
            qibuild.deploy.deploy(tmp, args.url, use_rsync=use_rsync, port=args.port)
        print

    if not args.single:
        ui.info(ui.green, ":: ", "Deploying projects")
    # Deploy projects: install them inside a 'deploy' dir inside the build dir,
    # then deploy this dir to the target
    for (i, project) in enumerate(projects):
        ui.info(ui.green, "*", ui.reset,
                "(%i/%i)" % (i+1, len(projects)),
                ui.green, "Deploying project", ui.blue, project.name,
                ui.green, "to", ui.blue, url)
        destdir = os.path.join(project.build_directory, "deploy")
        #create folder for project without install rules
        qibuild.sh.mkdir(destdir, recursive=True)
        toc.install_project(project, destdir, prefix="/",
                            runtime=True, num_jobs=args.num_jobs,
                            split_debug=True)
        qibuild.deploy.deploy(destdir, args.url, use_rsync=use_rsync, port=args.port)
        qibuild.deploy.generate_debug_scripts(toc, project.name, args.url)
