#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Deploy and install a package to a target """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys

import qipkg.parsers
import qipkg.package
import qisys.command
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.default_parser(parser)
    qipkg.parsers.pkg_parser(parser)
    qisys.parsers.deploy_parser(parser)
    parser.add_argument("pkg_path_or_pml")


def do(args):
    """ Main Entry Point """
    urls = qisys.parsers.get_deploy_urls(args)
    pkg_path_or_pml = args.pkg_path_or_pml
    if pkg_path_or_pml.endswith(".pkg"):
        pkg_path = pkg_path_or_pml
    elif pkg_path_or_pml.endswith(".pml"):
        pml_path = pkg_path_or_pml
        pkg_path = qisys.script.run_action("qipkg.actions.make_package",
                                           [pml_path],
                                           forward_args=args)
    else:
        sys.exit("Please use a .pml or a .pkg as argument")
    for url in urls:
        deploy(pkg_path, url)


def deploy(pkg_path, url):
    """ Deploy """
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
        return
    rm_cmd = ["ssh", "%s@%s" % (url.user, url.host),
              "rm", os.path.basename(pkg_path)]
    qisys.command.call(rm_cmd)


def _install_package(url, pkg_name, pkg_path):
    """ Install Package """
    # TODO: This will need NAOqi authentication
    import qi
    session = qi.Session()
    session.connect("tcp://%s:9559" % (url.host))
    package_manager = session.service("PackageManager")
    ui.info(ui.blue, "::", ui.reset, ui.bold, "Removing previous installation of the package")
    try:
        package_manager.removePkg(pkg_name)
    except Exception:
        pass
    ui.info(ui.blue, "::", ui.reset, ui.bold, "Installing package")
    ret = package_manager.install(
        "/home/%s/%s" % (url.user, os.path.basename(pkg_path)))
    ui.info("PackageManager returned:", ret)
