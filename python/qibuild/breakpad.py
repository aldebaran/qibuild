## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import subprocess

from qisys import ui
import qisys.archive
import qisys.sh
import qibuild.gdb
import qibuild.cmake

def dump_symbols_from_binary(binary, pool_dir, dump_syms_executable=None):
    """ Dump sympobls from the binary.
    Results can be found in
    <pool_dir>/<binary name>/<id>/<binary name>.sym

    """
    cmd = [dump_syms_executable, binary]
    ui.debug(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    if process.returncode != 0:
        ui.error("Failed to dump symbols", err)
        return

    # First line looks like:
    # MODULE Linux x86_64  ID  binary
    lines = out.splitlines()
    first_line = lines[0]
    uuid = first_line.split()[3]
    name = first_line.split()[4]

    to_make = os.path.join(pool_dir, name, uuid)
    qisys.sh.mkdir(to_make, recursive=True)
    with open(os.path.join(to_make, name + ".sym"), "w") as fp:
        fp.write(out)

def strip_binary(binary, strip_executable=None):
    if not strip_executable:
        strip_executable = qisys.command.find_program("strip", raises=True)
    cmd = [strip_executable, binary]
    qisys.command.call(cmd)

def gen_symbol_archive(project, base_dir=None, output=None, file_list=None):
    build_dir = project.build_directory
    strip_executable = qibuild.cmake.get_binutil("strip", build_dir=build_dir)
    dump_syms_executable = qibuild.cmake.get_cached_var(build_dir,
                                                        "DUMP_SYMS_EXECUTABLE")
    if not dump_syms_executable:
        dump_syms_executable = qisys.command.find_program("dump_syms", raises=True)
    dirname = os.path.dirname(output)
    basename = os.path.basename(output)
    name, _ = os.path.splitext(basename)
    pool_dir = os.path.join(dirname, name)
    binaries = list()
    for filename in file_list:
        full_path = os.path.join(base_dir, filename.lstrip("/"))
        if os.path.isfile(full_path) and qibuild.gdb.is_elf(full_path):
            binaries.append(full_path)
    for binary in binaries:
        print "dumping", binary
        dump_symbols_from_binary(binary, pool_dir,
                                 dump_syms_executable=dump_syms_executable)
        print "stripping", binary
        strip_binary(binary, strip_executable=strip_executable)

    qisys.archive.compress(pool_dir, output=output, flat=True)
    qisys.sh.rm(pool_dir)
    return output
