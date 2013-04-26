## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Deploy project(s) on a remote target

All deployed material is installed in the location 'path' on
the target 'hostname'.

Examples:

  qibuild deploy foobar john@mytarget:deployed

Installs everything on the target 'mytarget' in the
'deployed' directory from the 'john' 's home.

  qibuild deploy foobar john@mytarget:/tmp/foobar

Installs everything on the target 'mytarget' in the
'/tmp/foobar' directory.
"""

import os

from qisys import ui
import qibuild
import qisys.sh
import qibuild.deploy

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.project_parser(parser, positional=False)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("deploy options")
    group.add_argument("url", help="remote target url: user@hostname:path")
    group.add_argument("--url", dest="urls", action="append", help="urls")
    group.add_argument("--split-debug", action="store_true", default=True,
                        dest="split_debug", help="split debug symbols. "
                        "Enable remote debuging")
    group.add_argument("--no-split-debug", action="store_false",
                        dest="split_debug", help="do not split debug symbols. "
                        "Remote debugging won't work")

def find_rsync_or_scp(toc, raises=True):
    """ Return True if rsync is present.
    False if scp is present.
    Otherwise raise or return None depending of raises argument.
    """
    rsync = qisys.command.find_program("rsync", env=toc.build_env)
    if rsync:
        return True

    ui.warning("Please install rsync to get faster synchronisation")
    scp = qisys.command.find_program("scp", env=toc.build_env)
    if scp:
        return False

    if raises:
        raise Exception("Could not find rsync nor scp")

    return None

def do(args):
    """Main entry point."""
    urls = list()
    urls.append(args.url)
    if args.urls:
        urls.extend(args.urls)

    urls = [qibuild.deploy.parse_url(x) for x in urls]

    toc = qibuild.toc.toc_open(args.worktree, args)
    ui.info(ui.green, "Current worktree:", ui.reset, ui.bold, toc.worktree.root)
    if toc.active_config:
        ui.info(ui.green, "Active configuration: ",
                ui.blue, "%s (%s)" % (toc.active_config, toc.build_type))

    use_rsync = find_rsync_or_scp(toc)

    # Resolve deps:
    (packages, projects) = qibuild.cmdparse.deps_from_args(toc, args)

    # List projects, packages and urls related to deploy
    if not args.single:
        ui.info(ui.green, "The following projects")
        for project in projects:
            ui.info(ui.green, " *", ui.blue, project.name)

        if packages:
            ui.info(ui.green, "and the following packages")
            for package in packages:
                ui.info(" *", ui.blue, package.name)

        ui.info(ui.green, "will be deployed to")
        for url in urls:
            ui.info(ui.blue, url["given"])

    # Deploy packages: install all of them in the same temp dir, then
    # deploy this temp dir to the target
    if not args.single and packages:
        ui.info(ui.green, ":: ", "Deploying packages")
        with qisys.sh.TempDir() as tmp:
            for (i, package) in enumerate(packages, start=1):
                toc.toolchain.install_package(package.name, tmp, runtime=True)
                for url in urls:
                    ui.info(ui.green, "*", ui.reset,
                            "(%i/%i)" % (i, len(projects)),
                            ui.green, "Deploying package", ui.blue, package.name,
                            ui.green, "to", ui.blue, url["given"])
                    url_to_deploy = '%(login)s@%(url)s:%(dir)s' % url
                    qibuild.deploy.deploy(tmp, remote_url=url_to_deploy,
                            port=url.get("port", 22), use_rsync=use_rsync)

    if not args.single:
        ui.info(ui.green, ":: ", "Deploying projects")
    # Deploy projects: install them inside a 'deploy' dir inside the build dir,
    # then deploy this dir to the target
    deployed_list = list()
    for (i, project) in enumerate(projects, start=1):
        ui.info(ui.green, "*", ui.reset,
                "(%i/%i)" % (i, len(projects)),
                ui.green, "Deploying project", ui.blue, project.name,
                ui.green, "to", ui.blue, *[x["given"] for x in urls])
        destdir = os.path.join(project.build_directory, "deploy")
        #create folder for project without install rules
        qisys.sh.mkdir(destdir, recursive=True)
        toc.install_project(project, destdir, prefix="/",
                            runtime=True, num_jobs=args.num_jobs,
                            split_debug=args.split_debug)
        ui.info(ui.green, "Sending binaries to target...")
        for url in urls:
            url_to_deploy = '%(login)s@%(url)s:%(dir)s' % url
            qibuild.deploy.deploy(destdir, remote_url=url_to_deploy,
                    port=url.get("port", 22), use_rsync=use_rsync)
        if not args.split_debug:
            continue
        gdb_script, message = qibuild.deploy.generate_debug_scripts(toc, project.name,
                                                                    args.url,
                                                                    deploy_dir=destdir)

        bindir = os.path.join(destdir, "bin")
        binaries = list()
        if os.path.exists(bindir):
            binaries = [x for x in os.listdir(bindir)]
            binaries = [x for x in binaries if os.path.isfile(os.path.join(bindir, x))]
            binaries = [os.path.join("bin", x) for x in binaries]
        deployed_list.append((project, binaries, gdb_script, message))
    if not args.split_debug:
        return
    ui.info(ui.green, ":: ", "Deployed projects")
    for (i, deployed) in enumerate(deployed_list, start=1):
        project, binaries, gdb_script, message = deployed
        if not binaries:
            ui.info(ui.green, "*", ui.reset,
                    "(%i/%i)" % (i, len(projects)),
                    ui.green, "Project", ui.blue, project.name,
                    ui.green, "- No executable deployed")
            continue
        binaries = '\n'.join(ui.indent_iterable(binaries))
        ui.info(ui.green, "*", ui.reset,
                "(%i/%i)" % (i, len(projects)),
                ui.green, "Project", ui.blue, project.name,
                ui.green, "- Deployed binaries:",
                ui.reset, "\n%s" % binaries)
        if gdb_script:
            ui.info(ui.green, "*", ui.reset,
                    "To remotely debug a binary from the above list, run:")
            ui.info("    %s <binary>" % gdb_script)
        else:
            ui.warning(message)
