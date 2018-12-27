#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Convert a Package to QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import json
import fnmatch
import qisys.sh
import qisys.qixml
import qisys.command
from qisys import ui
from qisys.qixml import etree
import qibuild.cmake.modules
from qibuild.cmake.modules import add_cmake_module_to_archive
from qitoolchain.binary_package import convert_to_qibuild, open_package


def convert_package(package_path, name, interactive=False):
    """ Convert Package. """
    dest_dir = os.path.dirname(package_path)
    package = open_package(package_path)
    with qisys.sh.TempDir() as tmp:
        qibuild_package_path = convert_to_qibuild(package, output_dir=tmp)
        add_cmake_module_to_archive(qibuild_package_path, name, interactive=interactive)
        src = os.path.abspath(qibuild_package_path)
        dst = os.path.join(dest_dir, os.path.basename(qibuild_package_path))
        dst = os.path.abspath(dst)
        qisys.sh.mv(src, dst)
        qibuild_package_path = dst
    return qibuild_package_path


def conan_json_exists(package_path):
    """ Check whether the conanbuildinfo file exists. """
    conanbuildinfo_json = os.path.join(package_path, "conanbuildinfo.json")
    return os.path.isfile(conanbuildinfo_json)


def load_conan_json(package_path):
    """ Load the conanbuildinfo file as a dict and return it. """
    conanbuildinfo_json = os.path.join(package_path, "conanbuildinfo.json")
    with open(conanbuildinfo_json, 'r') as f:
        info = json.load(f)
        return info


def convert_from_conan(package_path, name, version="0.0.1"):
    """ Convert a conan build output directory to a qibuild package. """
    assert conan_json_exists(package_path), "{} not found".format(os.path.join(package_path, "conanbuildinfo.json"))
    info = load_conan_json(package_path)
    settings = info.get("settings")
    ui.info(ui.white, "Compiled on {} {} with {} version {}".format(settings.get("os"), settings.get("arch"),
                                                                    settings.get("compiler"),
                                                                    settings.get("compiler.version")))
    ui.info(ui.white, "Compiled in {} with {} ".format(settings.get("build_type"), settings.get("compiler.libcxx")))
    ui.info("Exposed librairies:")
    for n, deps in enumerate(info.get("dependencies")):
        ui.info_count(n, len(info.get("dependencies")), ui.blue, "{}@{}".format(deps.get("name"), deps.get("version")))
        _generate_conan_share_cmake(package_path, deps)
    if sys.platform == "darwin":
        _fix_rpaths(os.path.join(package_path, "lib"))
    _add_conan_package_xml(package_path, name, info, version)
    res = _compress_package(package_path, name, settings, version)
    ui.info(ui.green, "Archive generated in", res)
    return res


def _generate_conan_share_cmake(package_path, deps):
    """ Copy qibuild cmake module files. """
    name = deps.get("name")
    cmake_path = os.path.join(package_path, "share", "cmake")
    qisys.sh.mkdir(cmake_path, recursive=True)
    cmake_path = qibuild.cmake.modules.generate_cmake_module(package_path, name, deps)
    ui.info(ui.green, "CMake module generated in", ui.reset, ui.bold, cmake_path)


def _add_conan_package_xml(package_path, name, info, version):
    """ Write an xml file to descibe the package. """
    package_xml = os.path.join(package_path, "package.xml")
    ui.info(" -> Create package.xml for {}".format(name))
    root = etree.Element('package')
    root.set("name", name)
    root.set("version", version)
    root.set("target", info.get("settings").get("os"))
    child = etree.Element("licence", text="BSD")
    root.append(child)
    qisys.qixml.write(root, package_xml)


def _compress_package(package_path, name, settings, version):
    """ Form the name and create the archive. """
    parts = [name, settings.get("os"), settings.get("arch"), version]
    archive_name = "-".join(parts) + ".zip"
    output = os.path.join(os.getcwd(), archive_name)
    return qisys.archive.compress(package_path, flat=True, output=output, quiet=True, display_progress=True)


def _fix_rpaths(package_path):
    """ Search all dylib in lib directory and fix rpaths. """
    ui.info("Fix RPATH for", package_path, "librairies")
    # pylint: disable=W0612
    for root, dirs, files in os.walk(package_path):
        for basename in files:
            if basename.endswith("dylib"):
                ui.debug("Fixing RPATH for", basename)
                filename = os.path.join(root, basename)
                _fix_rpath(filename, package_path)


def _fix_rpath(binary_path, package_path):
    """ Fix the input dylib rpath and install name. """
    if not os.path.exists(binary_path):
        raise ValueError("file not found")
    if qisys.command.check_is_in_path("otool"):
        ui.warning("RPATH could not be fixed, otool is missing")
        return
    cmd = ['otool', '-L', binary_path]
    otool = qisys.command.check_output(cmd)
    ui.debug("Original RPATH:", otool)
    lines = otool.splitlines()
    for line in lines[1:]:
        dep = line.split()[0].strip()
        if not os.path.exists(dep):
            lib_name = os.path.basename(dep)
            lib_abs_path = None
            # pylint: disable=W0612
            for root, dirs, files in os.walk(package_path):
                for basename in files:
                    filename = os.path.join(root, basename)
                    if fnmatch.fnmatch(basename, lib_name):
                        lib_abs_path = filename
            if not lib_abs_path:
                continue
            lib_rel_path = os.path.relpath(lib_abs_path, package_path)
            if 'bin' in binary_path:
                new_rpath = "@executable_path/../%s" % lib_rel_path
            elif '/lib/' in binary_path:
                new_rpath = "@rpath/%s" % lib_rel_path
            else:
                new_rpath = '@loader_path/../%s' % lib_rel_path
            cmd = ['install_name_tool', '-change', dep, new_rpath, binary_path]
            qisys.command.call(cmd, ignore_ret_code=True)

    # Update binary install name
    cmd = ['install_name_tool', '-id', "@rpath/%s" % os.path.basename(binary_path), binary_path]
    otool = qisys.command.check_output(cmd)
    ui.debug("Install name:", otool)

    # Check result
    cmd = ['otool', '-L', binary_path]
    otool = qisys.command.check_output(cmd)
    ui.debug("Modified RPATH:", otool)
