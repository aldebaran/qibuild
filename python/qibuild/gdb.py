## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Tools for the GNU debbugger

"""

import os
import subprocess

from qisys import ui
import qisys.sh
import qisys.command

def is_elf(filename):
    """ Check that a file is in the efl format

   """
    with open(filename, "rb") as fp:
        data = fp.read(4)
    return data == "\x7fELF"

def contains_debug_info(filename, objdump=None):
    """ Check that an elf contains debug info

    """
    if not objdump:
        objdump = "objdump"
    retcode = subprocess.call([objdump, "-j", ".debug_info", "-h", filename],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return (retcode == 0)


def split_debug(base_dir, objcopy=None, objdump=None):
    """ Split the debug information out of all the binaries in
    lib/ and bin/

    The debug information will be put in a .debug directory next
    to the executable

    <base_dir>/bin/foo
    <base_dir>/bin/.debug/foo

    Also uses objcopy so that the binaries and libraries still remain
    usable with gdb

    :param:  the objcopy executable to use. (defaults to
     the first objcopy executable found in PATH)


    """
    if objcopy is None:
        objcopy = "objcopy"
    if objdump is None:
        objdump = "objdump"
    def _get_binaries(path):
        res = list()
        for root, _, filenames in os.walk(path):
            if os.path.basename(root) == ".debug":
                continue
            for filename in filenames:
                full_path = os.path.join(root, filename)
                if is_elf(full_path):
                    res.append(full_path)
        return res
    binaries = list()
    bin_dir = os.path.join(base_dir, "bin")
    lib_dir = os.path.join(base_dir, "lib")
    binaries.extend(_get_binaries(bin_dir))
    binaries.extend(_get_binaries(lib_dir))

    for src in binaries:
        rel_name = os.path.relpath(src, base_dir)
        if not contains_debug_info(src, objdump=objdump):
            ui.info("-- Already stripped", rel_name)
            continue
        src_stat = os.stat(src)
        dirname, basename = os.path.split(src)
        debug_dir = os.path.join(dirname, ".debug")
        qisys.sh.mkdir(debug_dir)
        dest = os.path.join(src, debug_dir, basename)
        to_run = list()
        to_run.append([objcopy, "--only-keep-debug", src, dest])
        to_run.append([objcopy, "--strip-debug", "--strip-unneeded",
                                "--add-gnu-debuglink=%s" % dest, src])
        try:
            for cmd in to_run:
                qisys.command.check_output(cmd, stderr=subprocess.STDOUT)
            ui.info("-- Debug info extracted for", rel_name)
        except qisys.command.CommandFailedException as e:
            ui.error("Error while extracting debug for %s" % os.path.relpath(src, base_dir))
            ui.error(str(e))
        # After the commands have run, utime of the file has changed, causing
        # cmake to re-install the libraries. Which is not cool ...
        # So set back mtime to its previous value:
        os.utime(src, (src_stat.st_atime, src_stat.st_mtime))

if __name__ == "__main__":
    import sys
    split_debug(sys.argv[1])
