## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module contains helpers for generating, checking CMake modules.

"""

import os
import re
import sys

from qisys import ui
import qisys
import qibuild


def _find_path_best_matches(path_list, filename_regex):
    """Return the list of path whose their basename match the given regular
    expression.

    """
    matches = list()
    if path_list is None or len(path_list) == 0:
        return matches
    regex = r"(" + "|".join(filename_regex) + ")"
    regex = re.compile(regex, re.IGNORECASE)
    # pep8-ignore: E501
    matches = [item for item in path_list if regex.search(os.path.basename(item))]
    matches.sort()
    return matches


def _find_headers(path_list):
    """Return the list of headers found in the given path list.

    """
    extensions = ["\.h$", "\.hh$", "\.hpp$"]
    hdrs     = _find_path_best_matches(path_list, extensions)
    return hdrs


def _get_header_relative_path(header):
    """Return the header path from the include directory

    """
    prefix = r".*?" + os.sep + "?include" + os.sep
    hdr_path = re.sub(prefix, "", header)
    return hdr_path


def _find_libraries(path_list, platform=None):
    """Return the list of libraries found in the given path list.

    """
    extensions = None
    if platform is None:
        platform = sys.platform
    if platform.startswith("linux"):
        extensions = ["\.a", "\.so"]
    elif platform.startswith("darwin"):
        extensions = ["\.a", "\.dylib"]
    elif platform.startswith("win"):
        extensions = ["\.lib", "\.dll"]
    else:
        mess = "Unsupported platform"
        raise Exception(mess)
    regex = r"(" + "|".join(extensions) + ")$"
    libs  = _find_path_best_matches(path_list, [regex])
    libs_ = dict()
    for lib in libs:
        key = re.sub(regex, "", lib)
        if not key in libs_.keys():
            libs_[key] = list()
        libs_[key].append(lib)
    return libs_.values()


def _get_library_name(library):
    """Return the library name for the library file path

    """
    lib_name = os.path.basename(library)
    lib_name = lib_name.rsplit('.', 1)[0]
    lib_name = re.sub("^lib", "", lib_name)
    return lib_name


def find_cmake_module_in(path_list):
    """Return the list of CMake modules found in the given path list.

    :param path_list: list of the content to be searched

    :return: list of found CMake modules

    """
    pattern = r"^(find.*?|.*?-config).cmake$"
    modules = _find_path_best_matches(path_list, [pattern])
    return modules


def find_matching_qibuild_cmake_module(package_name):
    """Return the list of CMake modules provided by qiBuild and matching names.

    :param names: list of names used for matching

    :return: list of matching CMake modules

    """
    root = qibuild.__path__[0].rsplit(os.sep, 2)[0]
    root = os.path.join(root, 'cmake', 'qibuild', 'modules')
    root = os.path.abspath(root)
    path_list = qisys.sh.ls_r(root)
    #name = re.sub("^lib", "(lib)?", name)
    #name = re.sub("[^a-zA-Z0-9]+", ".*?", name)
    modules = find_cmake_module_in(path_list)
    modules = _find_path_best_matches(modules, [package_name])
    return modules


def check_for_module_generation(package_root, package_name):
    """Return the status of the search of matching CMake modules already
    provided by either the package itself or qiBuild.

    The status can have the following values: "provided_by_package", or
    "provided_by_qibuild" or "nonexistent".

    :param name:           list of names of the CMake module to be checked
    :param root_dir:       base directory of the package to be search
                           (default: None)
    :param path_list:      list of the content of the package to be search
                           (default: None)
    :param module_package: list of CMake modules found in the package
                           (default: None)
    :param module_qibuild: list of CMake modules provided by qiBuild
                           (default: None)

    :return: the tuple (module check status,
                        list of modules provided by package,
                        list of modules provided by qiBuild)

    """
    path_list = qisys.sh.ls_r(package_root)
    modules_package = find_cmake_module_in(path_list)
    modules_qibuild = find_matching_qibuild_cmake_module(package_name)
    prefix = r".*?" + os.sep + "?usr" + os.sep
    # pep8-ignore: E501
    modules_package = [re.sub(prefix, "", item) for item in modules_package]
    # pep8-ignore: E501
    modules_qibuild = [re.sub(prefix, "", item) for item in modules_qibuild]
    status = "nonexistent"
    if modules_qibuild:
        status = "provided_by_qibuild"
    if modules_package:
        status = "provided_by_package"
    return (status, modules_package, modules_qibuild)


def show_existing_modules(name, modules_package, modules_qibuild):
    """Print the CMake modules found in the package itself or provided by
    qiBuild for this package.

    :param name:           package nane
    :param module_package: list of CMake modules found in the package
    :param module_qibuild: list of CMake modules provided by qiBuild

    """
    if len(modules_package) > 0:
        modules = "\n".join("  {0}".format(x) for x in modules_package)
        message = """\
Package '{0}' already provides the following CMake module(s):
{1}
""".format(name, modules)
        qisys.ui.info(message)
    if len(modules_qibuild) > 0:
        modules = "\n".join("  {0}".format(x) for x in modules_qibuild)
        message = """\
qiBuild already provides the following CMake module(s) for the package '{0}':
{1}
""".format(name, modules)
        qisys.ui.info(message)
    return


def _generate_template(name, header, libraries):
    """Generate a template of CMake module.

    :param name:      package name
    :param header:    header location (used by 'fpath')
    :param libraries: list of libraries  (used by 'flib')

    :return: the template string of the CMake module

    """
    prefix = name.upper()
    # pep8-ignore: E501
    content = """\
## ----------------------------------------------------------------------------
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
## ----------------------------------------------------------------------------
"""
    content += """
## CMake module for {name}

clean({prefix})
""".format(name=name, prefix=prefix)
    if header is not None:
        content += """
fpath({prefix} {header})
""".format(prefix=prefix, header=_get_header_relative_path(header))
    if len(libraries) > 0:
        libnames = [_get_library_name(lib[0]) for lib in libraries]
        libnames = list(set(libnames))
        for libname in libnames:
            content += """\
flib({prefix} {libname})
""".format(prefix=prefix, libname=libname)
    content += """
export_lib({prefix})
""".format(prefix=prefix)
    return content

def _ask_module_info(name, headers, libraries):
    """Interactively get the required CMake module data.

    :param name:        package name
    :param prefix:      CMake module prefix
    :param header:      header location (used by 'fpath')
    :param libraries:   list of libraries  (used by 'flib')

    :return: a tuple (name, prefix, header, libraries)

    """
    patterns = [name]
    header = None
    if len(headers) > 0:
        patterns = [pattern.lower() for pattern in patterns]
        patterns = [re.sub("[-_]", ".?", pattern) for pattern in patterns]
        patterns = [re.sub("^lib", "(lib)?", pattern) for pattern in patterns]
        try:
            header_  = _find_path_best_matches(headers, patterns)[0]
            headers.remove(header_)
            headers.insert(0, header_)
            question = "Which is the main header?"
            header   = qisys.interact.ask_choice(headers, question)
        except IndexError:
            pass
    libs = None
    if len(libraries) > 0:
        libs = list()
        question = """\
Which libraries do you want to declare in the CMake module?\
"""
        qisys.ui.info(question)
        for lib_static_shared in libraries:
            question = ", ".join(lib_static_shared)
            answer   = qisys.interact.ask_yes_no(question, default=True)
            if answer:
                libs.append([lib_static_shared[0]])
    return (name, header, libs)

def _edit_template(name, template, package_path_list):
    """Handle interactive edition of the CMake module template.

    :param name:              package name
    :param template:          input CMake module template
    :param package_path_list: list of the content of the package
                              (default: None)

    :return: the template string

    """
    # pep8-ignore: E501
    question = "Edit generated CMake module for {0} (highly recommended)?".format(name)
    answer   = qisys.interact.ask_yes_no(question, default=True)
    if not answer:
        return template
    answer = False
    if package_path_list is not None:
        # pep8-ignore: E501
        question = "Would you like to list the package content before?".format(name)
        answer   = qisys.interact.ask_yes_no(question, default=True)
    if answer:
        message = """\
Package content:
{0}

Press enter to launch the editor.\
""".format("\n".join("  " + x for x in package_path_list))
        qisys.ui.info(message)
        qisys.interact.read_input()
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    editor = qibuild_cfg.defaults.env.editor
    if not editor:
        editor = qisys.interact.get_editor()
    editor_path = qisys.command.find_program(editor)
    with qisys.sh.TempDir() as tmp_dir:
        cmake_module = os.path.join(tmp_dir, 'tmp-module.cmake')
        with open(cmake_module, 'w') as module_file:
            module_file.write(template)
        qisys.command.call([editor_path, cmake_module])
        with open(cmake_module, 'r') as module_file:
            module = module_file.read()
    return module


# pylint: disable-msg=R0913
def generate_module(name, headers, libraries, path_list=None):
    """Generate a template of CMake module from all information passed.

    :param name:        package name
    :param header:      header location (used by 'fpath')
    :param libraries:   list of libraries  (used by 'flib')
    :param path_list:   list of the content of the package
                        (default: None)
    :return: the tuple (package name,
                        template string of the CMake module)

    """
    libs     = None
    header   = None
    if ui.CONFIG["interactive"]:
        template_data = _ask_module_info(name, headers, libraries)
        name, header, libs = template_data
    if header is None and len(headers) > 0:
        header = headers[0]
    if libs is None:
        libs = libraries
    template = _generate_template(name, header, libs)
    if ui.CONFIG["interactive"]:
        module = _edit_template(name, template, path_list)
    return module


def add_cmake_module_to_directory(directory, name):
    """Generate a template of CMake module from the content of directory.

    :param directory:   base directory of the package
    :param name:        package name
    """
    status, modules_package, modules_qibuild = \
        check_for_module_generation(directory, name)
    if status != "nonexistent":
        show_existing_modules(name, modules_package, modules_qibuild)
        if ui.CONFIG["interactive"]:
            answer = qisys.interact.ask_yes_no("""\
Do you want to generate a new CMake module for {0}?\
""".format(name), default=False)
            if not answer:
                return
        else:
            return
    path_list = qisys.sh.ls_r(directory)
    headers   = _find_headers(path_list)
    libraries = _find_libraries(path_list)
    module    = generate_module(name, headers, libraries, path_list=path_list)
    write_cmake_module(directory, name, module)


def add_cmake_module_to_archive(archive, name):
    """Generate a template of CMake module from an archive.
    The archive is updated in-place

    :param archive:     archive path of the package
    :param name:        package name
                        (default: None)
    :param prefix:      CMake module prefix
                        (default: None)

    """
    algo   = qisys.archive.guess_algo(archive)
    with qisys.sh.TempDir() as work_dir:
        # pep8-ignore: E501
        root_dir = qisys.archive.extract(archive, work_dir, algo=algo, quiet=True)
        if name is None:
            name = os.path.basename(root_dir)
        add_cmake_module_to_directory(root_dir, name)
        res = qisys.archive.compress(root_dir)
        qisys.sh.mv(res, archive)


def write_cmake_module(package_root, name, contents):
    """Write the CMake module content in the right location.

    This writes the CMake module in::

      base_dir/prefix/share/cmake/self.prefix.lower()/self.prefix.lower()-config.cmake

    :param base_dir: root directory (the package installation DESTDIR)
    :return: the path of the generated CMake module

    """
    module_name = name + "-config.cmake"
    module_path = os.path.join(package_root, "share", "cmake", name)
    qisys.sh.mkdir(module_path, recursive=True)
    module_path = os.path.join(module_path, module_name)
    with open(module_path, "w") as module_file:
        module_file.write(contents)
    return module_path
