#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Modules """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import qisys.sh
import qisys.interact
from qisys import ui
import qibuild.config


def find_libs(directory, info=None):
    """ Find Libs """
    lib_directory = os.path.join(directory, "lib")
    res = list()
    if not os.path.exists(lib_directory):
        return list()
    candidates = os.listdir(lib_directory)
    for candidate in candidates:
        if info:
            clues = info.get("libs")
            for c in clues:
                if candidate.endswith((".so", ".a", ".lib", ".dylib")) and c.lower() in candidate.lower():
                    ui.debug("found:", candidate)
                    res.append("lib/" + candidate)
        else:
            if candidate.endswith((".so", ".a", ".lib", ".dylib")):
                res.append("lib/" + candidate)
    return sorted(res)


def generate_cmake_module(directory, name, info=None):
    """ Generate CMake Module """
    libraries = find_libs(directory, info)
    libs_string = ""
    for library in libraries:
        libs_string += "  ${_root}/%s\n" % library
    libs_string = libs_string[:-1]  # remove trailing \n
    template = """\
set(_root "${CMAKE_CURRENT_LIST_DIR}/../../..")
get_filename_component(_root ${_root} ABSOLUTE)

set(@NAME@_LIBRARIES
@libraries@
  CACHE INTERNAL "" FORCE
)

set(@NAME@_INCLUDE_DIRS
  ${_root}/include
  CACHE INTERNAL "" FORCE
)

# qi_persistent_set(@NAME@_DEPENDS "")
export_lib(@NAME@)
"""
    contents = template.replace("@NAME@", name.upper())
    contents = contents.replace("@libraries@", libs_string)
    to_make = os.path.join(directory, "share", "cmake", name)
    qisys.sh.mkdir(to_make, recursive=True)
    to_write = os.path.join(to_make, "%s-config.cmake" % name.lower())
    with open(to_write, "w") as fp:
        fp.write(contents)
    return to_write


def edit_module(module_path):
    """ Handle interactive edition of the CMake module. """
    question = "Edit generated CMake module (highly recommended)?"
    answer = qisys.interact.ask_yes_no(question, default=True)
    if not answer:
        return
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    editor = qibuild_cfg.defaults.env.editor
    if not editor:
        editor = qisys.interact.get_editor()
    editor_path = qisys.command.find_program(editor)
    qisys.command.call([editor_path, module_path])


def add_cmake_module_to_archive(archive_path, name, interactive=True):
    """ Add CMake Module To Archive """
    algo = qisys.archive.guess_algo(archive_path)
    with qisys.sh.TempDir() as work_dir:
        root_dir = qisys.archive.extract(archive_path, work_dir, algo=algo,
                                         quiet=True, strict_mode=False)
        if name is None:
            name = os.path.basename(root_dir)
        module = generate_cmake_module(root_dir, name)
        if interactive:
            edit_module(module)
        res = qisys.archive.compress(root_dir, flat=True)
        qisys.sh.mv(res, archive_path)
