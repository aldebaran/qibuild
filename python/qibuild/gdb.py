## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Tools for the GNU debugger

"""

import os
import subprocess

from qisys import ui
import qisys.sh
import qisys.command


def contains_debug_info(filename, objdump=None):
    """ Check that an elf contains debug info

    """
    if not objdump:
        objdump = "objdump"
    retcode = subprocess.call([objdump, "-j", ".debug_info", "-h", filename],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return (retcode == 0)

def split_debug(src, objcopy=None, objdump=None):
    """ Split the debug information in the `src` binary.

    The debug information will be put in a .debug directory next
    to the executable

    <base_dir>/bin/foo
    <base_dir>/bin/.debug/foo

    Also uses objcopy so that the binaries and libraries still remain
    usable with gdb
    """
    if objcopy is None:
        objcopy = "objcopy"
    if objdump is None:
        objdump = "objdump"
    if not contains_debug_info(src, objdump=objdump):
        ui.info("-- Already stripped", src)
        return
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
        ui.info("-- Debug info extracted for", src)
    except qisys.command.CommandFailedException as e:
        ui.error("Error while extracting debug for %s" % src)
        ui.error(str(e))
    # After the commands have run, utime of the file has changed, causing
    # cmake to re-install the libraries. Which is not cool ...
    # So set back mtime to its previous value:
    os.utime(src, (src_stat.st_atime, src_stat.st_mtime))


if __name__ == "__main__":
    import sys
    split_debug(sys.argv[1])
