## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Deploy and install a package to a target

"""

import os
import sys
import zipfile

from qisys import ui
import qisys.command
import qisys.parsers
import qipkg.package

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    qisys.parsers.deploy_parser(parser)
    parser.add_argument("pkg_path")

def do(args):
    urls = qisys.parsers.get_deploy_urls(args)
    pkg_path = args.pkg_path
    for url in urls:
        deploy(pkg_path, url)

def deploy(pkg_path, url):
    ui.info(ui.green, "Deploying",
            ui.reset, ui.blue, pkg_path,
            ui.reset, ui.green, "to",
            ui.reset, ui.blue, url.as_string)
    pkg_name = qipkg.package.name_from_archive(pkg_path)
    scp_cmd = ["scp",
                pkg_path,
                "%s@%s:" % (url.user, url.host)]
    qisys.command.call(scp_cmd)

    try:
        _install_package(url, pkg_name, pkg_path)
    except Exception as e:
        ui.error("Unable to install package on target")
        ui.error("Error was: ", e)

    rm_cmd = ["ssh", "%s@%s" % (url.user, url.host),
                "rm", os.path.basename(pkg_path)]
    qisys.command.call(rm_cmd)

def _install_package(url, pkg_name, pkg_path):
    import qi
    app = qi.Application()
    session = qi.Session()
    session.connect("tcp://%s:9559" % (url.host))
    package_manager = session.service("PackageManager")
    try:
        package_manager.removePkg(pkg_name)
    except:
        pass
    ret = package_manager.install(
            "/home/%s/%s" % (url.user, os.path.basename(pkg_path)))
    ui.info("PackageManager returned: ", ret)
