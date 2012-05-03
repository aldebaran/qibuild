## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to handle .dylib and frameworks on Mac

"""

import os
import re
import logging
import subprocess

import qibuild.sh

LOGGER = logging.getLogger(__name__)

def fix_dylibs(sdk_dir, paths=None):
    """ Create symlinks to every framework
    and every dynamic library in the SDK_DIR,
    so that running the newly compiled executables
    work when setting
    DYLD_LIBRARY_PATH to sdk_dir/lib and
    DYLD_FRAMEWORK_PATH to sdk_dir

    """
    # This directory may not exist, so create it:
    qibuild.sh.mkdir(os.path.join(sdk_dir, "lib"), recursive=True)

    for path in paths:
        frameworks = os.listdir(path)
        frameworks = [x for x in frameworks if x.endswith(".framework")]
        for framework in frameworks:
            src  = os.path.join(path    , framework)
            dest = os.path.join(sdk_dir, framework)
            qibuild.sh.rm(dest)
            os.symlink(src, dest)
        lib_dir = os.path.join(path, "lib")
        if not os.path.exists(lib_dir):
            continue
        dylibs = os.listdir(lib_dir)
        dylibs = [x for x in dylibs if ".dylib" in x]
        for dylib in dylibs:
            src  = os.path.join(path   , "lib", dylib)
            dest = os.path.join(sdk_dir, "lib", dylib)
            qibuild.sh.rm(dest)
            os.symlink(src, dest)
