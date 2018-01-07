## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a rpm package, based on a .spec file """

import os
import sys

from qisys import ui
import qisys.sh
import qisys.parsers
import qibuild.parsers
import subprocess

def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("-s", "--specfile", action="store",
        dest="specfile", help="Specify the name of the specfile in the package directory")
    parser.add_argument("-i", "--install-dir", action="store",
        dest="install", help="Specify the install directory")
    parser.set_defaults(specfile="default.spec", install="None")

def do(args):
    """ Main entry point """
    cmake_builder = qibuild.parsers.get_build_worktree(args)

    install_dir = os.path.join(cmake_builder.root, args.install)
    package_path = os.path.join(cmake_builder.root, "package")
    spec_file_path = os.path.join(package_path, args.specfile)
    rpm_build_dir = os.path.join(package_path, "rpm")
    _do_package(install_dir, spec_file_path, rpm_build_dir, package_path, args)

def _do_package(install_dir, spec_file_path, rpm_build_dir, package_path, args):
    prepare(package_path, rpm_build_dir)
    if args.specfile == "default.spec" and not os.path.exists(spec_file_path):
        create_spec(spec_file_path)
        ui.info(ui.green, "Default specfile generated in", ui.reset, ui.bold, package_path)
        sys.exit()
    subprocess.call(["cp", spec_file_path, os.path.join(rpm_build_dir, "SPECS", args.specfile)])
    subprocess.call(["tar", "cjvf", os.path.join(rpm_build_dir, "SOURCES", "install.tbz"), install_dir])
    if subprocess.call(["rpmbuild", "-D", "_topdir " + rpm_build_dir, "-ba",
            os.path.join(rpm_build_dir, "SPECS", args.specfile)]) == 0:
        ui.info(ui.green, "Package generated in", ui.reset, ui.bold, rpm_build_dir)
    else:
        ui.info(ui.red, "Package failed to generate")

def prepare(package_path, rpm_build_dir):
    if not os.path.exists(package_path):
        os.makedirs(package_path)
    qisys.sh.rm(rpm_build_dir)
    os.makedirs(rpm_build_dir)
    for direct in ["BUILD", "RPMS", "SOURCES", "SPECS", "clearSRPMS", "tmp"]:
        dir_build = os.path.join(rpm_build_dir, direct)
        if not os.path.exists(dir_build):
            os.makedirs(dir_build)

def create_spec(spec_file_path):
    with open(spec_file_path,"w") as spec_file:
        spec_file.write("""
Name: 
Version:
Release:
Summary:
Group:
License:
URL:
Source: install.tbz
#BuildRequires:
#Requires:
%%description
%%prep
%%setup -c SPECS
%%build
%%install
%%files
%%doc
%%changelog
""")
