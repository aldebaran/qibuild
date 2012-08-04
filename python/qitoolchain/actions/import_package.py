## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Import a binary package into a toolchain.
"""

import os
import subprocess

import qibuild
import qitoolchain
import qitoolchain.binary_package

_CMAKE_MODULE_PKG_LIST = """
Package {0} already provides the following CMake module(s):
{1}
You can find it/them at the above location(s) from the package installation
directory (run 'qitoolchain info' to get it).
"""

_CMAKE_MODULE_QIBUILD_LIST = """
qiBuild already provides the following CMake module(s) for the package {0}:
{1}
"""

_CMAKE_TPL_WARNING = """\
## -----------------------------------------------------------------------------
##
## WARNING:
##
##     This is just a templated CMake module generated from the content of the
##     package.
##
##     It is highly recommended to double-check the exactness of this generated
##     file.
##
##     To get help writing this cmake module, check out:
##     http://www.aldebaran-robotics.com/documentation/qibuild/ref/cmake/api/find.html
##
## -----------------------------------------------------------------------------
"""

_CMAKE_TPL_PROLOGUE = """
## CMake module for {name}

clean({prefix})

## Please check the headers provided within the package and set the fpath
## accordingly:
fpath({prefix} {header})

## Please check the libraries provided within the package and set the flib
## accordingly:
"""

_CMAKE_TPL_LIBDECL = """\
flib({prefix} {libname})
"""

_CMAKE_TPL_EPILOGUE = """
export_lib({prefix})
"""

_MESSAGE_START = "Importing '{1}' in the toolchain '{0}' ..."

_MESSAGE_END = "Package '{1}' has successfully been added to the toolchain '{0}'."

def _get_header(root_dir, pattern):
    """ Return a header provided by a package extracted in 'root_dir'.

    Try to find the header matching the pattern (most of the time, this pattern
    is the package name).

    :return: a header file name

    """
    inc_dir = os.path.join(root_dir,'usr', 'include')
    headers = dict()
    # Find all headers provided by the package
    for root, _, files in os.walk(inc_dir):
        for file_ in files:
            headers[file_] = os.path.join(root, file_)
    # Get all headers that match the pattern, then:
    # - if 1 or more matches, pick just one;
    # - otherwise, pick the first one
    pick_one = [ x for x in headers.keys() if pattern in x ]
    if len(pick_one) > 0:
        pick_one.sort()
        key = pick_one[0]
        header = headers[key]
    else:
        headers = headers.values()
        headers.sort()
        header = headers[0]
    # Remove the '/usr/include' prefix of the header path
    header = header.split(inc_dir + os.sep, 1).pop()
    return header

def _get_libraries(root_dir):
    """ Return the list of the libraries provided by the package

    :return: a list of library names

    """
    def _is_lib(filename):
        ret = filename.startswith('lib') and \
            ( filename.endswith('.so') or filename.endswith('.a') )
        return ret
    lib_dir = os.path.join(root_dir, 'lib')
    if os.path.exists(lib_dir):
        mess = "Error: Found system libraries"
        raise Exception(mess)
    lib_dir = os.path.join(root_dir, 'usr', 'lib')
    libs = os.listdir(lib_dir)
    libs = [ x for x in libs if os.path.isfile(os.path.join(lib_dir, x)) ]
    libs = [ x.rsplit('.', 1)[0][3:] for x in libs if _is_lib(x) ]
    libs = list(set(libs))
    return libs

def _get_content(root_dir):
    """ Return a list of the content of the package

    :return: a list of the content of the package

    """
    content = list()
    for root, _, files in os.walk(root_dir):
        content.extend([ os.path.join(root, x) for x in files ])
    return content

def _get_existing_cmake_module(module_names, root_dir):
    """ Search for existing cmake module file provided by either:

    - the package itself (scanning the subtree from root_dir);
    - or qiBuild.

    :return: a tuple of list: (provided by the package, provided by qiBuild)

    """
    from_package = list()
    from_qibuild = list()
    # Search for CMake module provided by package itself
    search_root = os.path.join(root_dir, 'usr', 'share', 'cmake')
    prefix = os.path.join(root_dir, 'usr') + os.sep
    for root, _, files in os.walk(search_root):
        for file_ in files:
            if file_.endswith('-config.cmake'):
                from_package.append(os.path.join(root, file_).replace(prefix, ''))
    # Search for CMake module provided by qiBuild
    qibuild_dir = qibuild.__path__[0].rsplit(os.sep, 2)[0]
    search_root = os.path.join(qibuild_dir, 'cmake', 'qibuild', 'modules')
    for root, _, files in os.walk(search_root):
        for _file in files:
            for module_name in module_names:
                if _file.endswith('-config.cmake') and module_name in _file:
                    from_qibuild.append(os.path.join(root, _file))
    return (from_package, from_qibuild)

def _check_for_cmake_module(root_dir, module_names):
    """ Check for existing cmake module file provided by either:

    - the package itself (scanning the subtree from root_dir);
    - or qiBuild.

    :return: a tuple (found boolean, provided by the package, provided by qiBuild)

    """
    from_package, from_qibuild = _get_existing_cmake_module(module_names, root_dir)
    found = len(from_qibuild) > 0 or len(from_package) > 0
    return (found, from_package, from_qibuild)

def _generate_cmake_module(root_dir, module_names):
    """ Generate the cmake module file scanning the subtree from root_dir.

    """
    pkg_content = _get_content(root_dir)
    print "\nPackage content:\n\n"
    for item in pkg_content:
        print item.replace(root_dir, '')

    cmake_module_name = module_names[0]
    if cmake_module_name.startswith('lib'):
        cmake_module_name = cmake_module_name[3:]
    cmake_module_filename = '{0}-config.cmake'.format(cmake_module_name)
    cmake_module_dir = os.path.join(root_dir, 'usr', 'share', 'cmake', 'modules')
    cmake_module_path = os.path.join(cmake_module_dir, cmake_module_filename)

    module = { 'name'   : module_names[0],
               'prefix' : cmake_module_name.upper(),
               'header' : _get_header(root_dir, cmake_module_name),
               'libs'   : _get_libraries(root_dir),
               }
    content = _CMAKE_TPL_WARNING + _CMAKE_TPL_PROLOGUE
    content = content.format(**module)
    for lib in module['libs']:
        module['libname'] = lib
        content += _CMAKE_TPL_LIBDECL.format(**module)
    content += _CMAKE_TPL_EPILOGUE.format(**module)
    qibuild.sh.mkdir(cmake_module_dir, recursive=True)
    with open(cmake_module_path, 'w') as fout:
        fout.write(content)

    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    editor = qibuild_cfg.defaults.env.editor
    if not editor:
        editor = qibuild.interact.get_editor()

    editor_path = qibuild.command.find_program(editor)
    subprocess.call([editor_path, cmake_module_path])

    return

def _fix_pkgtree(root_dir):
    """ Make the package tree comply with qiBuild.

    """
    for item in os.listdir(os.path.join(root_dir, 'usr')):
        src = os.path.join(root_dir, 'usr', item)
        dst = os.path.join(root_dir, item)
        if os.path.exists(dst):
            mess = "Destination already exists"
            raise Exception(mess)
        qibuild.sh.mv(src, dst)
    qibuild.sh.rm(os.path.join(root_dir, 'usr'))
    return

def _convert_to_qibuild(qipkg_dir, package, package_names):
    """ Convert a binary package into a qiBuild package.

    :return: path to the qiBuild package

    """
    with qibuild.sh.TempDir() as work_dir:
        root_dir = package.extract(work_dir)
        _checks = _check_for_cmake_module(root_dir, package_names)
        cmake_found, from_pkg, from_qibuild = _checks
        prefix_ = os.path.join(work_dir, 'usr') + os.sep
        if cmake_found:
            if len(from_pkg) > 0:
                list_ = [ x.replace(prefix_, '') for x in from_pkg ]
                list_ = ''.join([ '  {0}\n'.format(x) for x in list_ ])
                print _CMAKE_MODULE_PKG_LIST.format(package_names[0], list_)
            if len(from_qibuild) > 0:
                list_ = ''.join([ '  {0}\n'.format(x) for x in from_pkg ])
                print _CMAKE_MODULE_QIBUILD_LIST.format(package_names[0], list_)
        else:
            _generate_cmake_module(root_dir, package_names)

        _fix_pkgtree(root_dir)
        qipkg_path = qibuild.archive.zip(root_dir)
        qipkg_file = os.path.basename(qipkg_path)
        qibuild.sh.mv(qipkg_path, qipkg_dir)
        qipkg_path = os.path.join(qipkg_dir, qipkg_file)
        qipkg_path = os.path.abspath(qipkg_path)
    return qipkg_path


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("package_name", metavar='NAME',
        help="The name of the package", nargs='?')
    parser.add_argument("package_path", metavar='PATH',
        help="The path to the package")
    return

def do(args):
    """ Import a binary package into a toolchain

    - Check that there is a CMake module into the binary package
    - Add the qiBuild package to the cache
    - Add the qiBuild package from cache to toolchain

    """
    tc_name = qitoolchain.toolchain_name_from_args(args)
    tc = qitoolchain.get_toolchain(tc_name)

    package_name = args.package_name
    package_path = args.package_path

    with qibuild.sh.TempDir() as tmp:
        package = qitoolchain.binary_package.open_package(package_path)

    package_metadata = package.get_metadata()

    if package_name is None:
        package_name = package_metadata['name']

    package_names = [ package_name, package_metadata['name'] ]
    package_names = list(set(package_names))

    # extract it to the default packages path of the toolchain
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc.name)
    dest = os.path.join(tc_packages_path, package_name)
    qibuild.sh.rm(dest)
    qibuild.ui.info(_MESSAGE_START.format(tc.name, package_name))
    with qibuild.sh.TempDir() as tmp:
        qibuild_pkg = _convert_to_qibuild(tmp, package, package_names)
        extracted = qibuild.archive.extract(qibuild_pkg, tmp, quiet=True)
        qibuild.sh.install(extracted, dest, quiet=True)
    qibuild_package = qitoolchain.Package(package_name, dest)
    tc.add_package(qibuild_package)
    qibuild.ui.info(_MESSAGE_END.format(tc.name, package_name))
