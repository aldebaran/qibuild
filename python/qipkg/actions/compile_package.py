# Copyright (c) 2015 Aldebaran Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Update a package by replacing python source files by their byte-code equivalent """

import os
import zipfile
import py_compile
import sys
import re

from qisys import ui
import qisys.qixml
import qisys.parsers


def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    parser.add_argument("pkg_path")
    parser.add_argument("-o", "--output")


def do(args):
    pkg_path = args.pkg_path
    output_path = args.output

    to_add = list()

    # Extract the package to a temp path
    with qisys.sh.TempDir() as tmp_path:
        archive = zipfile.ZipFile(pkg_path)
        qisys.archive.extract(pkg_path, tmp_path,
                              algo="zip", strict_mode=False)
        archive.close()

        # Compile python files, remove python sources
        _compile_python_files(tmp_path)

        # Adapt execPath of Python services
        _update_python_services(tmp_path)

        # add everything from the temp path
        ui.info(ui.bold, "-> Compressing package ...")
        for root, _, filenames in os.walk(tmp_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, tmp_path)
                to_add.append((full_path, rel_path))

        if not output_path:
            output_path = os.path.join(os.getcwd(), os.path.basename(pkg_path))

        archive = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)
        for i, (full_path, rel_path) in enumerate(to_add):
            n = len(to_add)
            if sys.stdout.isatty():
                percent = float(i) / n * 100
                sys.stdout.write("Done: %.0f%%\r" % percent)
                sys.stdout.flush()
            archive.write(full_path, rel_path)
        archive.close()

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
        execStart = service.attrib['execStart']
        execStart = re.sub(r".py\b", r".pyc", execStart)

        match_object = service_file_regexp.match(execStart)
        if match_object is None:
            continue
        service_file_path = match_object.group(1)

        # update execStart command only if it points on a file inside the package
        if os.path.exists(os.path.join(package_path, service_file_path)):
            service.set('execStart', execStart)

    qisys.qixml.write(tree, manifest_path, encoding="utf-8")


def _print_progress_message(value, max_value, prefix):
    if sys.stdout.isatty():
        percent = float(value) / max_value * 100
        sys.stdout.write(prefix + ": %.0f%%\r" % percent)
        sys.stdout.flush()
