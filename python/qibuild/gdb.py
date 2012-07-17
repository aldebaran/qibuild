## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Tools for the GNU debbugger

"""

import os
import logging

from qibuild import ui
import qibuild.sh
import qibuild.command


def split_debug(base_dir, objcopy=None):
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
    def _get_binaries(dir):
        res = list()
        for root, directories, filenames in os.walk(dir):
            if os.path.basename(root) == ".debug":
                continue
            for filename in filenames:
                res.append(os.path.join(root, filename))
        return res
    binaries = list()
    bin_dir = os.path.join(base_dir, "bin")
    lib_dir = os.path.join(base_dir, "lib")
    binaries.extend(_get_binaries(bin_dir))
    binaries.extend(_get_binaries(lib_dir))

    for src in binaries:
        dirname, basename = os.path.split(src)
        debug_dir = os.path.join(dirname, ".debug")
        qibuild.sh.mkdir(debug_dir)
        dest = os.path.join(src, debug_dir, basename)
        to_run = list()
        to_run.append([objcopy, "--only-keep-debug", src, dest])
        to_run.append([objcopy, "--strip-debug", "--strip-unneeded",
                                "--add-gnu-debuglink=%s" % dest, src])
        retcode = 0
        #check if we need to do something
        #if mtime of src and dest are the same continue, else do the work and set
        #the mtime of dest to the one of src.
        stsrc = os.stat(src)
        stdst = None
        if os.path.exists(dest):
            stdst = os.stat(dest)
        if stdst and stsrc.st_mtime == stdst.st_mtime:
            ui.info("Debug info up-to-date for %s" % os.path.relpath(src, base_dir))
            continue
        for cmd in to_run:
            retcode = 0
            # FIXME: we should of course not try to split debug info twice, but
            # that's a hard problem
            retcode += qibuild.command.call(cmd, ignore_ret_code=True, quiet=True)
        if retcode == 0:
            os.utime(dest, (stsrc.st_atime, stsrc.st_mtime))
            ui.info("Debug info extracted for %s" % os.path.relpath(src, base_dir))
        else:
            ui.error("Error while extracting debug for %s" % os.path.relpath(src, base_dir))

if __name__ == "__main__":
    import sys
    split_debug(sys.argv[1])

