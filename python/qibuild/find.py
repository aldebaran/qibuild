## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Find a target given its name

"""

import os
import platform

def _library_prefix(os_name=None):
    """ Return suitable library prefix used on current OS.
    """
    # Os variable can be forced for test purpose
    if os_name is None:
        os_name = platform.system()
    if os_name == "Windows":
        return ""
    else:
        return "lib"

def _library_suffix(dynamic, debug=True, os_name=None):
    """ Return suitable library suffix used on current OS.
    """
    # Os variable can be forced for test purpose
    if os_name is None:
        os_name = platform.system()

    # On Windows system, debug libraries wears "_d" suffix.
    debug_suffix = ""
    if debug is True:
        debug_suffix = "_d"

    if os_name == "Windows" and dynamic is True:
        return debug_suffix + ".dll"
    if os_name == "Windows" and dynamic is False:
        return debug_suffix + ".lib"
    if os_name == "Linux" and dynamic is True:
        return ".so"
    if os_name in ("Linux", "Mac") and dynamic is False:
        return ".a"
    if os_name == "Mac" and dynamic:
        return ".dylib"
    return ""

def _binary_suffix(dynamic=True, debug=True, os_name=None):
    """ Return suitable binary suffix used on current OS.
    """
    # Os variable can be forced for test purpose
    if os_name is None:
        os_name = platform.system()

    # On Windows system, debug binaries wear "_d" suffix.
    debug_suffix = ""
    if debug is True:
        debug_suffix = "_d"

    # On Windows system, binaries wear ".exe" extention
    if os_name == "Windows":
        return debug_suffix + ".exe"
    return ""

def find(projects, name, debug=True):
    """ Search package directly in build directories so,
        this way, we are sure that returned path really point
        on package.
    """
    as_lib = library_name(name, debug=debug)
    for project in projects:
        candidates = list()
        sdk_directory = project.sdk_directory
        bin_dir = os.path.join(sdk_directory, "bin")
        bin_name = binary_name(name, debug=debug)
        candidates.append(os.path.join(bin_dir, bin_name))
        if os.name == 'nt':
            # a dll is in bin too
            lib_name = library_name(name, debug=debug, dynamic=True)
            candidates.append(os.path.join(bin_dir, lib_name))

        for dynamic in True, False:
            lib_dir = os.path.join(project.sdk_directory, "lib")
            lib_name = library_name(name, debug=debug, dynamic=dynamic)
            candidates.append(os.path.join(lib_dir, lib_name))

        print candidates
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

def binary_name(name, dynamic=True, debug=True, os_name=None):
    """ Return exact binary name for current OS.
    """
    return name + _binary_suffix(dynamic=dynamic, debug=debug, os_name=os_name)

def library_name(name, dynamic=True, debug=True, os_name=None):
    """ Return exact library name for current OS.
    """
    return _library_prefix(os_name) + name + _library_suffix(dynamic=dynamic, debug=debug,
                                                             os_name=os_name)

