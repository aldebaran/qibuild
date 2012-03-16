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

def find_missing_libs_and_frameworks(executable):
    """ Run otool -L and returns a list of problematic libs and frameworks

    """
    missing_libs = list()
    missing_frameworks = list()
    LOGGER.debug("checking %s", executable)
    cmd = ["otool", "-L", executable]
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    (out, err) = process.communicate()
    if err:
        LOGGER.warning("Error when runnning otool -L on %s", executable)
        LOGGER.warning("Error was: %s", err)
        return
    #pylint: disable-msg=E1103
    out_lines = out.splitlines()
    out_lines = out_lines[1:]
    libs_to_check = list()
    for line in out_lines:
        # Line looks like:
        #     /pat/to/foo/dylib  (compatibility version ...)
        libs_to_check.append(line.split("(")[0].strip())
    res = list()
    for lib in libs_to_check:
        # Absolute path (/usr/lib/libstdc++.lib, /usr/local/mydep.dylib)
        if os.path.isabs(lib):
            if not os.path.exists(lib):
                missing_libs.append(os.path.basename(lib))
        if ".framework" in lib:
            # find the framework name
            match = re.search("/?(\w*)\.framework/?", lib)
            if match:
                missing_frameworks.append(match.groups()[0] + ".framework")
        elif "@executable_path" in lib:
            # A qibuild dep ("@executable_path/../lib/libfoo.dylib")
            if "@executable_path/../lib/" in lib:
                missing_libs.append(lib[24:])
        else:
            #Tthird party dep  with no install name tool at all ("boost_filesystem.dylib")
            missing_libs.append(lib)
    LOGGER.debug("missing libs: %s", missing_libs)
    LOGGER.debug("missing frameworks: %s", missing_frameworks)
    return (missing_libs, missing_frameworks)

def find_lib(lib_name, paths):
    """ Find a libname in a list of paths

    libnane will be searh in each path, in
      * path
      * path/lib

    """
    for path in paths:
        full_path = os.path.join(path, "lib", lib_name)
        if os.path.exists(full_path):
            return full_path
        full_path = os.path.join(path, lib_name)
        if os.path.exists(full_path):
            return full_path

def find_framework(name, paths):
    """ Find a framewok in a list of paths

    """
    for path in paths:
        full_path = os.path.join(path, name)
        if os.path.exists(full_path):
            return full_path

def fix_dylibs(sdk_dir, paths=None):
    """ Copy the .dylibs and the .framework from the toolchain packages
    and the other build dirs into the SDK directory, so that
    running the executable just works.

    Also run install_name_tool to fix 3rd party install name tool
    that do not match "@executable/../lib"

    """
    # Look for executables in build/sdk/bin, run otool -L,
    # and try to create symlinks if there is a problem
    bin_dir = os.path.join(sdk_dir, "bin")
    if not os.path.exists(bin_dir):
        return
    binaries = os.listdir(bin_dir)
    binaries = [os.path.join(bin_dir, x) for x in binaries]
    for binary in binaries:
        if not qibuild.sh.is_executable_binary(binary):
            continue
        (missing_libs, missing_frameworks) = \
            find_missing_libs_and_frameworks(binary)
        for missing_lib in missing_libs:
            lib_path = qibuild.dylibs.find_lib(missing_lib, paths)
            if lib_path:
                # Create a symlink
                dest = os.path.join(sdk_dir, "lib", missing_lib)
                to_create = os.path.dirname(dest)
                qibuild.sh.mkdir(to_create, recursive=True)
                if not os.path.exists(dest):
                    LOGGER.debug("symlink: %s -> %s", dest, lib_path)
                    os.symlink(lib_path, dest)
        for missing_framework in missing_frameworks:
            framework_path = find_framework(missing_framework, paths)
            if framework_path:
                # Create a symlink
                dest = os.path.join(sdk_dir, missing_framework)
                to_create = os.path.dirname(dest)
                qibuild.sh.mkdir(to_create, recursive=True)
                if not os.path.exists(dest):
                    LOGGER.debug("symlink: %s -> %s", dest, framework_path)
                    os.symlink(framework_path, dest)
