#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Tools to deploy files to remote targets """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
from collections import OrderedDict

import qisys.command
from qisys import ui

FILE_SETUP_GDB = """\
# gdb script generated by qiBuild

set architecture i386
set verbose
set sysroot %(sysroot)s
set solib-search-path %(solib_search_path)s
"""

FILE_SETUP_TARGET_GDB = """\
# gdb script generated by qiBuild

source %(source_file)s
target remote %(remote_gdb_address)s
"""

FILE_REMOTE_GDBSERVER_SH = """\
#!/bin/bash
# script generated by qiBuild
# run a gdbserver on the remote target

here=$(cd $(dirname $0) ; pwd)

if [ "$#" -lt "1" ] ; then
  echo "please specify the binary to run"
  exit 1
fi

binary=$1
shift 1
echo ""
echo "To connect to this gdbserver launch the following command in another terminal:"
echo "  %(gdb)s -x \"${here}/setup_target.gdb\" \"${here}/${binary}\""
echo ""

echo ssh -p %(port)s %(host)s -- gdbserver %(gdb_listen)s "%(remote_dir)s/${1}"
"""


def _generate_setup_gdb(dest, sysroot="\"\"", solib_search_path=None, remote_gdb_address=""):
    """ Generate a script that connects a local gdb to a gdbserver. """
    if not solib_search_path:
        solib_search_path = list()
    source_file = os.path.abspath(os.path.join(dest, "setup.gdb"))
    with open(source_file, "w+") as f:
        f.write(FILE_SETUP_GDB % {
            'sysroot': sysroot,
            'solib_search_path': ":".join(solib_search_path)
        })
    with open(os.path.join(dest, "setup_target.gdb"), "w+") as f:
        f.write(FILE_SETUP_TARGET_GDB % {
            'source_file': source_file,
            'remote_gdb_address': remote_gdb_address
        })
    return ["setup_target.gdb", "setup.gdb"]


def _generate_run_gdbserver_binary(dest, host, gdb, gdb_listen, remote_dir, port):
    """ Generate a script that run a program on the robot in gdbserver. """
    if remote_dir is None:
        remote_dir = "."
    remote_gdb_script_path = os.path.join(dest, "remote_gdbserver.sh")
    with open(remote_gdb_script_path, "w+") as f:
        f.write(FILE_REMOTE_GDBSERVER_SH % {'host': host,
                                            'gdb_listen': gdb_listen,
                                            'remote_dir': remote_dir,
                                            'gdb': gdb,
                                            'port': port})
    os.chmod(remote_gdb_script_path, 0o755)
    return [os.path.basename(remote_gdb_script_path)]


def _get_subfolder(directory):
    """ Get SubFolders """
    res = list()
    for root, __dirs, __files in os.walk(directory):
        new_root = os.path.abspath(root)
        if not os.path.basename(new_root).startswith(".debug"):
            res.append(new_root)
    return res


def _generate_solib_search_path(cmake_builder, project_name):
    """ Generate the solib_search_path useful for gdb. """
    res = list()
    dep_types = ["build", "runtime"]
    build_worktree = cmake_builder.build_worktree
    project = build_worktree.get_build_project(project_name)
    deps_solver = cmake_builder.deps_solver
    dep_projects = deps_solver.get_dep_projects([project], dep_types)
    for dep_project in dep_projects:
        dep_build_dir = dep_project.build_directory
        dep_lib_dir = os.path.join(dep_build_dir, "deploy", "lib")
        res.extend(_get_subfolder(dep_lib_dir))
    dep_packages = deps_solver.get_dep_packages([project], dep_types)
    for dep_package in dep_packages:
        dep_lib_dir = os.path.join(dep_package.path, "lib")
        res.extend(_get_subfolder(dep_lib_dir))
    # Idiom to sort an iterable preserving order
    return list(OrderedDict.fromkeys(res))


def generate_debug_scripts(cmake_builder, deploy_dir, project_name, url, port=22):
    """ Generate all scripts needed for debug. """
    host = url.host
    remote_directory = url.remote_directory
    solib_search_path = _generate_solib_search_path(cmake_builder, project_name)
    sysroot = None
    gdb = None
    message = None
    toolchain = cmake_builder.toolchain
    if toolchain:
        sysroot = toolchain.get_sysroot()
    if sysroot:
        # assume cross-toolchain
        gdb = toolchain.get_cross_gdb()
        if gdb:
            message = "Cross-build. Using the cross-debugger provided by the toolchain."
        else:
            message = "Remote debugging not available: No cross-debugger found in the cross-toolchain"
    else:
        # assume native toolchain
        sysroot = "\"\""
        gdb = qisys.command.find_program("gdb")
        if gdb:
            message = "Native build. Using the debugger provided by the system."
        else:
            message = "Debugging not available: No debugger found in the system."
    if not gdb:
        ui.warning(message)
        return None
    if toolchain:
        sysroot = toolchain.get_sysroot()
    to_deploy = list()
    setup_gdb = _generate_setup_gdb(deploy_dir, sysroot=sysroot,
                                    solib_search_path=solib_search_path,
                                    remote_gdb_address="%s:2159" % host)
    gdb_script = _generate_run_gdbserver_binary(deploy_dir, gdb=gdb, gdb_listen=":2159",
                                                host=host, port=port,
                                                remote_dir=remote_directory)
    ui.info(message)
    to_deploy = setup_gdb + gdb_script
    return to_deploy
