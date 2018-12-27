#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Breakpad """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import stat
import subprocess

import qisys.sh
import qisys.archive
import qisys.command
from qisys import ui


def is_elf(filename):
    """ Check that a file is in the elf format. """
    with open(filename, "rb") as fp:
        data = fp.read(4)
    fp.close()
    return data == "\x7fELF"


def is_macho(filename):
    """ Check that a file is in the Mach-O format. """
    with open(filename, "rb") as fp:
        data = fp.read(2)
    fp.close()
    return data == '\xcf\xfa'


def is_exe(filename):
    """ Check that a file is a Windows executable. """
    return filename.endswith((".exe", ".dll"))


def can_be_dumped(filename):
    """" Check that symbols can be dumped from the given file """
    st = os.lstat(filename)
    # File must be a regular file
    if not stat.S_ISREG(st.st_mode):
        return False
    # File must be an executable
    if sys.platform.startswith("linux"):
        return is_elf(filename)
    if sys.platform == "darwin":
        return is_macho(filename)
    if os.name == "nt":
        return is_exe(filename)
    return False


def dump_symbols_from_binary(binary, pool_dir, build_config=None):
    """
    Dump symbols from the binary.
    Results can be found in
    <pool_dir>/<binary name>/<id>/<binary name>.sym
    """
    dump_syms = qisys.command.find_program("dump_syms", raises=True, build_config=build_config)
    if sys.platform == "darwin":
        dsym = gen_dsym(binary)
        cmd = [dump_syms, dsym]
    else:
        cmd = [dump_syms, binary]
    ui.debug(cmd)
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except OSError as e:
        ui.error("Could not dump symbols", cmd, e)
        return
    dump_ok = True
    (out, err) = process.communicate()
    if process.returncode != 0:
        ui.error("Failed to dump symbols", err)
        dump_ok = False
    if sys.platform == "darwin":
        qisys.sh.rm(dsym)
    if not dump_ok:
        return
    # First line looks like:
    # MODULE Linux x86_64  ID  foo on linux
    # MODULE windows x86 ID foo.pdb on windows
    # path should be
    # pool/foo.pdb/ID/foo.sym on windows,
    # pool/foo/ID/foo.sym on linux
    lines = out.splitlines()
    first_line = lines[0]
    uuid = first_line.split()[3]
    name = first_line.split()[4]
    if os.name == "nt":
        basename = name.replace(".pdb", "")
    else:
        basename = name
    to_make = os.path.join(pool_dir, name, uuid)
    qisys.sh.mkdir(to_make, recursive=True)
    with open(os.path.join(to_make, basename + ".sym"), "w") as fp:
        fp.write(out)
    fp.close()


def strip_binary(binary, strip_executable=None, strip_args=None, build_config=None):
    """ Strip Binary """
    if not strip_executable:
        strip_executable = qisys.command.find_program("strip", raises=True, build_config=build_config)
    cmd = [strip_executable]
    if strip_args:
        cmd.extend(strip_args)
    cmd.append(binary)
    with qisys.sh.PreserveFileMetadata(binary):
        mode_rw = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
        os.chmod(binary, mode_rw)
        rc = qisys.command.call(cmd, ignore_ret_code=True)
    if rc != 0:
        ui.warning("Failed to strip symbols for", binary)


def gen_dsym(binary):
    """ Generate Dsym """
    cmd = ["dsymutil", binary]
    qisys.command.call(cmd)
    return binary + ".dSYM"


def dump_symbols_from_directory(root_dir, pool_dir, strip=True,
                                strip_exe=None, strip_args=None, build_config=None):
    """
    Dump symbols for every binary in the root dir.
    Assumes that dump_syms is in $PATH.
    If strip is True, also strip the binaries. (assumes that strip is in $PATH)
    """
    for (root, __directories, filenames) in os.walk(root_dir):
        for filename in filenames:
            full_path = os.path.join(root_dir, root, filename)
            if os.path.islink(full_path):
                continue
            if can_be_dumped(full_path):
                ui.info("dumping", full_path)
                dump_symbols_from_binary(full_path, pool_dir, build_config=build_config)
                if strip and os.name == "posix":
                    if sys.platform == "darwin":
                        strip_args = ["-u", "-r"]
                    else:
                        strip_args = list()
                    ui.info("stripping", full_path)
                    strip_binary(full_path, strip_executable=strip_exe,
                                 strip_args=strip_args, build_config=build_config)
    return pool_dir


def gen_symbol_archive(base_dir=None, output=None, strip=True,
                       strip_exe=None, strip_args=None, build_config=None):
    """ Generate a symbol archive from all the binaries in the base_dir """
    with qisys.sh.TempDir() as pool_dir:
        dump_symbols_from_directory(base_dir, pool_dir, strip=strip,
                                    strip_exe=strip_exe, strip_args=strip_args, build_config=build_config)
        qisys.archive.compress(pool_dir, output=output, flat=True)
    return output
