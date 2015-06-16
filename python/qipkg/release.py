# Copyright (c) 2015 Aldebaran Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Update a package by replacing python source files by their byte-code equivalent """

import os
import py_compile
import sys
import re

from qisys import ui
import qisys.qixml
import qisys.parsers


def make_release(pkg_path, output_path):
    # Extract the package to a temp path
    with qisys.sh.TempDir() as tmp_path:
        qisys.archive.extract(pkg_path, tmp_path,
                              algo="zip", strict_mode=False)

        # Compile python files, remove python sources
        _compile_python_files(tmp_path)

        # Adapt execPath of Python services
        _update_python_services(tmp_path)

        # add everything from the temp path
        qisys.archive.compress(tmp_path, output=output_path, flat=True)

    ui.info(ui.green, "Package compiled to", ui.reset,
            ui.bold, output_path)


def _compile_python_files(base_dir):
    for root, _, filenames in os.walk(base_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)

            # Compile Python files if the user asked for it
            _, ext = os.path.splitext(file_path)
            if ext == str(".py"):
                py_compile.compile(file_path, doraise="True")
                qisys.sh.rm(file_path)


def _update_python_services(package_path):
    service_file_regexp = re.compile(r"(?:.*\s)?(.*?\.pyc)\b")

    manifest_path = os.path.join(package_path, "manifest.xml")
    tree = qisys.qixml.read(manifest_path)

    root = tree.getroot()
    services = root.findall("services/service")
    for service in services:
        exec_start = service.attrib["execStart"]
        exec_start = re.sub(r".py\b", r".pyc", exec_start)

        match_object = service_file_regexp.match(exec_start)
        if match_object is None:
            continue
        service_file_path = match_object.group(1)

        # update execStart command only if it points on a file inside the package
        if os.path.exists(os.path.join(package_path, service_file_path)):
            service.set("execStart", exec_start)

    qisys.qixml.write(tree, manifest_path, encoding="utf-8")