# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Set of tools to handle .dylib and frameworks on Mac

"""

import os
import qisys.sh


def fix_dylibs(sdk_dir, paths=None):
    """ Create symlinks to every framework
    and every dynamic library in the SDK_DIR,
    so that running the newly compiled executables
    work when setting
    DYLD_LIBRARY_PATH to sdk_dir/lib and
    DYLD_FRAMEWORK_PATH to sdk_dir

    """
    # This directory may not exist, so create it:
    qisys.sh.mkdir(os.path.join(sdk_dir, "lib"), recursive=True)

    for path in paths:
        if not os.path.exists(path):
            continue
        frameworks = os.listdir(path)
        frameworks = [x for x in frameworks if x.endswith(".framework")]
        for framework in frameworks:
            src = os.path.join(path, framework)
            dest = os.path.join(sdk_dir, framework)
            qisys.sh.rm(dest)
            os.symlink(src, dest)
        lib_dir = os.path.join(path, "lib")
        if not os.path.exists(lib_dir):
            continue
        dylibs = os.listdir(lib_dir)
        dylibs = [x for x in dylibs if ".dylib" in x]
        for dylib in dylibs:
            src = os.path.join(path, "lib", dylib)
            dest = os.path.join(sdk_dir, "lib", dylib)
            if os.path.islink(src):
                # don't create recursive links
                continue
            # just re-create links if they already exist
            qisys.sh.rm(dest)
            os.symlink(src, dest)
