## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Find a package

"""

import sys
import os
import glob
import platform
import qibuild

from qisys import ui

def _library_prefix(os):
    """ Return suitable library prefix used on current OS.
    """
    if os is None:
        os = platform.system()

    if os == "Windows":
        return ""
    return "lib"

def _library_suffix(os, dynamic, debug):
    """ Return suitable library suffix used on current OS.
    """

    # Os variable can be forced for test purpose
    if os is None:
        os = platform.system()

    # On Windows system, debug libraries wears "_d" suffix.
    debug_suffix = ""
    if debug is True:
        debug_suffix = "_d"

    if os == "Windows" and dynamic is True:
        return debug_suffix + ".dll"
    if os == "Windows" and dynamic is False:
        return debug_suffix + ".lib"
    if os == "Linux" and dynamic is True:
        return ".so"
    if os == "Linux" and dynamic is False:
        return ".a"
    if os == "Mac":
        return ".dylib"
    return ""

def _binary_suffix(os, dynamic, debug):
    """ Return suitable binary suffix used on current OS.
    """
    # Os variable can be forced for test purpose
    if os is None:
        os = platform.system()

    # On Windows system, debug binaries wear "_d" suffix.
    debug_suffix = ""
    if debug is True:
        debug_suffix = "_d"

    # On Windows system, binaries wear ".exe" extention
    if os == "Windows":
        return debug_suffix + ".exe"
    return ""

def find(projects, package):
    """ Search package directly in build directories so,
        this way, we are sure that returned path really point
        on package.
    """
    for project in projects:
        bin = os.path.join(project.sdk_directory, "bin")
        bin = os.path.join(bin, binary_name(package))

        lib = os.path.join(project.sdk_directory, "lib")
        lib = os.path.join(lib, library_name(package))
        for files in glob.glob(bin):
            return bin
        for files in glob.glob(lib):
            return lib

def binary_name(name, dynamic=True, debug=False, os=None):
    """ Return exact binary name for current OS.
    """
    return name + _binary_suffix(os, dynamic, debug)

def library_name(name, dynamic=True, debug=False, os=None):
    """ Return exact library name for current OS.
    """
    return _library_prefix(os) + name + _library_suffix(os, dynamic, debug)
