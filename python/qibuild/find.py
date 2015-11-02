## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Find a target given its name

"""

import os
import platform

import qisys.sh

def find_lib(paths, name, debug=None, expect_one=True, shared=None):
    """ Find a library in a list of paths.

    :param: debug. If ``None``, looks for both debug and
                   release. If ``True``, only look for
                   a library built in debug, if ``False``,
                   only look for a library built in release.
                   (This is only relevant on Windows)

    :param expect_one:
        If True, raises:

         * NotFound if no match is found
         * MulipleFound if more than one match is found

        Otherwise return a list of matches

    """
    candidates = set()
    if debug is None:
        debug_cases = [True, False]
    else:
        debug_cases = [debug]

    if shared is None:
        shared_cases = [True, False]
    else:
        shared_cases = [shared]

    for debug in debug_cases:
        for shared in shared_cases:
            lib_name = library_name(name, shared=shared, debug=debug)
            for path in paths:
                lib_path = os.path.join(path, "lib", lib_name)
                candidates.add(lib_path)
                if os.name == 'nt' and shared:
                    # dlls can be in bin/ on windows:
                    lib_path = os.path.join(path, "bin", lib_name)
                    candidates.add(lib_path)

    return _filter_candidates(name, candidates, expect_one=expect_one)


def find_bin(paths, name, debug=None, expect_one=True):
    """ Find a binary in a list of paths.

    :param: debug. If ``None``, looks for both debug and
                   release. If ``True``, only look for
                   a binary built in debug, if ``False``,
                   only look for a binary built in release.
                   (This is only relevant on Windows)

    :param expect_one:
        If True, raises:

         * NotFound if no match is found
         * MulipleFound if more than one match is found

        Otherwise return a list of matches

    """
    candidates = set()
    if debug is None:
        debug_cases = [True, False]
    else:
        debug_cases = [debug]

    for debug in debug_cases:
        bin_name = binary_name(name, debug=debug)
        for path in paths:
            bin_path = os.path.join(path, "bin", bin_name)
            candidates.add(bin_path)

    return _filter_candidates(name, candidates, expect_one=expect_one)

def find(paths, name, debug=True, expect_one=True):
    """ Search a binary or a library given its name

    """
    bins = find_bin(paths, name, debug=debug, expect_one=False)
    libs = find_lib(paths, name, debug=debug, expect_one=False)
    candidates = bins + libs
    return _filter_candidates(name, candidates, expect_one=expect_one)



def binary_name(name, debug=True, os_name=None):
    """ Return exact binary name for current OS.
    """
    return name + _binary_suffix(debug=debug, os_name=os_name)

def library_name(name, shared=True, debug=True, os_name=None):
    """ Return exact library name for current OS.
    """
    return _library_prefix(os_name) + name + _library_suffix(shared=shared, debug=debug,
                                                             os_name=os_name)

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

def _library_suffix(shared=True, debug=True, os_name=None):
    """ Return suitable library suffix used on current OS.
    """
    # Os variable can be forced for test purpose
    if os_name is None:
        os_name = platform.system()

    # On Windows system, debug libraries wears "_d" suffix.
    debug_suffix = ""
    if debug is True:
        debug_suffix = "_d"

    if os_name == "Windows" and shared is True:
        return debug_suffix + ".dll"
    if os_name == "Windows" and shared is False:
        return debug_suffix + ".lib"
    if os_name == "Linux" and shared is True:
        return ".so"
    if os_name in ("Linux", "Darwin") and shared is False:
        return ".a"
    if os_name == "Darwin" and shared:
        return ".dylib"
    return ""

def _binary_suffix(debug=True, os_name=None):
    """ Return suitable binary suffix used on current OS.
    """
    # Os variable can be forced for test purpose
    if os_name is None:
        os_name = platform.system()

    # On Windows system, debug binaries wear "_d" suffix.
    debug_suffix = ""
    if debug is True:
        debug_suffix = "_d"

    # On Windows system, binaries wear ".exe" extension
    if os_name == "Windows":
        return debug_suffix + ".exe"
    return ""

def _filter_candidates(name, candidates, expect_one=True):
    res = [x for x in candidates if os.path.exists(x)]
    res = [qisys.sh.to_native_path(x) for x in res]
    if not expect_one:
        return res
    if expect_one and not res:
        raise NotFound(name)
    if len(res) > 1:
        raise MulipleFound(name, res)
    return res[0]


class NotFound(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "%s not found" % self.name

class MulipleFound(Exception):
    def __init__(self, name, res):
        self.name = name
        self.res = res

    def __str__(self):
        return """ \
Expecting only one result for {0}, got {1}
{2}
""".format(self.name, len(self.res), "\n".join(self.res))
