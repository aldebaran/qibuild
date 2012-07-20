## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module contains helpers for generating, checking CMake modules.

"""

import os
import re
import sys

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


def find_matching_qibuild_cmake_module(names):
    """Return the list of CMake modules provided by qiBuild and matching names.

    :param names: list of names used for matching

    :return: list of matching CMake modules

    """
    root = qibuild.__path__[0].rsplit(os.sep, 2)[0]
    root = os.path.join(root, 'cmake', 'qibuild', 'modules')
    root = os.path.abspath(root)
    path_list = qibuild.sh.ls_r(root)
    names = [re.sub("^lib", "(lib)?", name) for name in names]
    names = [re.sub("[^a-zA-Z0-9]+", ".*?", name) for name in names]
    names = list(set(names))
    modules = find_cmake_module_in(path_list)
    modules = _find_path_best_matches(modules, names)
    return modules


def check_for_module_generation(names, root_dir=None, path_list=None,
                                modules_package=None, modules_qibuild=None):
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
    if modules_package is None and modules_qibuild is None:
        if path_list is None:
            if root_dir is None:
                mess = "Wrong call: at least 1 argument should be not 'None'"
                raise Exception(mess)
            path_list = qibuild.sh.ls_r(root_dir)
        modules_package = find_cmake_module_in(path_list)
        modules_qibuild = find_matching_qibuild_cmake_module(names)
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


def show_exiting_modules(name, modules_package, modules_qibuild):
    """Print the CMake modules found in the package itself or provided by
    qiBuild for this package.

    :param name:           package nane
    :param module_package: list of CMake modules found in the package
    :param module_qibuild: list of CMake modules provided by qiBuild

    """
    if len(modules_package) > 0:
        modules = "\n".join(["  {0}".format(x) for x in modules_package])
        message = """\
Package '{0}' already provides the following CMake module(s):
{1}
""".format(name, modules)
        qibuild.ui.info(message)
    if len(modules_qibuild) > 0:
        modules = "\n".join(["  {0}".format(x) for x in modules_qibuild])
        message = """\
qiBuild already provides the following CMake module(s) for the package '{0}':
{1}
""".format(name, modules)
        qibuild.ui.info(message)
    return


def _generate_template(name, prefix, header, libraries):
    """Generate a template of CMake module.

    :param name:      package name
    :param prefix:    CMake module prefix
    :param header:    header location (used by 'fpath')
    :param libraries: list of libraries  (used by 'flib')

    :return: the template string of the CMake module

    """
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

def _ask_template_info(name, prefix, headers, libraries):
    """Interactively get the required CMake module data.

    :param name:        package name
    :param prefix:      CMake module prefix
    :param header:      header location (used by 'fpath')
    :param libraries:   list of libraries  (used by 'flib')

    :return: a tuple (name, prefix, header, libraries)

    """
    patterns = [name]
    question = "Enter the package name:"
    name     = qibuild.interact.ask_string(question, default=name)
    patterns.append(name)
    patterns = list(set(patterns))
    question = "Do you want to use '{0}' as CMake module name?"
    question = question.format(prefix)
    answer   = qibuild.interact.ask_yes_no(question, default=True)
    if not answer:
        question = "Enter the CMake module name (uppercase):"
        prefix   = qibuild.interact.ask_string(question, default=prefix)
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
            header   = qibuild.interact.ask_choice(headers, question)
        except IndexError:
            pass
    libs = None
    if len(libraries) > 0:
        libs = list()
        question = """\
Which libraries do you want to declare in the CMake module?\
"""
        qibuild.ui.info(question)
        for lib_static_shared in libraries:
            question = ", ".join(lib_static_shared)
            answer   = qibuild.interact.ask_yes_no(question, default=True)
            if answer:
                libs.append([lib_static_shared[0]])
    return (name, prefix, header, libs)

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
    answer   = qibuild.interact.ask_yes_no(question, default=True)
    if answer:
        answer = False
        if package_path_list is not None:
            # pep8-ignore: E501
            question = "Would you like to list the package content before?".format(name)
            answer   = qibuild.interact.ask_yes_no(question, default=True)
        if answer:
            message = """\
Package content:
{0}

Press enter to launch the editor.\
""".format("\n".join(["  " + x for x in package_path_list]))
            qibuild.ui.info(message)
            qibuild.interact.read_input()
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read()
        editor = qibuild_cfg.defaults.env.editor
        if not editor:
            editor = qibuild.interact.get_editor()
        editor_path = qibuild.command.find_program(editor)
        with qibuild.sh.TempDir() as tmp_dir:
            cmake_module = os.path.join(tmp_dir, 'tmp-module.cmake')
            with open(cmake_module, 'w') as module_file:
                module_file.write(template)
            qibuild.command.call([editor_path, cmake_module])
            with open(cmake_module, 'r') as module_file:
                template = module_file.read()
    return template


# pylint: disable-msg=R0913
def generate_template(name, prefix, headers, libraries, path_list=None,
                      interactive=True):
    """Generate a template of CMake module from all information passed.

    :param name:        package name
    :param prefix:      CMake module prefix
    :param header:      header location (used by 'fpath')
    :param libraries:   list of libraries  (used by 'flib')
    :param path_list:   list of the content of the package
                        (default: None)
    :param interactive: enable user interaction
                        (default: True)

    :return: the tuple (package name,
                        CMake module prefix,
                        template string of the CMake module)

    """
    libs     = None
    header   = None
    if prefix is None:
        prefix = name
    prefix   = prefix.upper()
    if interactive:
        template_data = _ask_template_info(name, prefix, headers, libraries)
        name, prefix, header, libs = template_data
    if header is None and len(headers) > 0:
        header = headers[0]
    if libs is None:
        libs = libraries
    prefix  = prefix.upper()
    template = _generate_template(name, prefix, header, libs)
    if interactive:
        template = _edit_template(name, template, path_list)
    return (name, prefix, template)


def generate_template_from_directory(directory, name, prefix=None,
                                     path_list=None, interactive=True):
    """Generate a template of CMake module from the content of directory.

    :param directory:   base directory of the package
    :param name:        package name
    :param prefix:      CMake module prefix
                        (default: None)
    :param path_list:   list of the content of the package
                        (default: None)
    :param interactive: enable user interaction
                        (default: True)

    :return: the tuple (package name,
                        CMake module prefix,
                        template string of the CMake module)

    """
    if path_list is None:
        path_list = qibuild.sh.ls_r(directory)
    headers   = _find_headers(path_list)
    libraries = _find_libraries(path_list)
    module    = generate_template(name, prefix, headers, libraries,
                                  path_list=path_list, interactive=interactive)
    return module


def generate_template_from_archive(archive, name=None, prefix=None,
                                   interactive=True):
    """Generate a template of CMake module from an archive.

    :param archive:     archive path of the package
    :param name:        package name
                        (default: None)
    :param prefix:      CMake module prefix
                        (default: None)
    :param interactive: enable user interaction
                        (default: True)

    :return: the tuple (package name,
                        CMake module prefix,
                        template string of the CMake module)

    """
    algo   = qibuild.archive.guess_algo(archive)
    module = None
    with qibuild.sh.TempDir() as work_dir:
        # pep8-ignore: E501
        root_dir = qibuild.archive.extract(archive, work_dir, algo=algo, quiet=True)
        if name is None:
            name = os.path.basename(root_dir)
        module = generate_template_from_directory(root_dir, name,
                                                  prefix=prefix,
                                                  interactive=interactive)
        return module


class CMakeModule(object):
    """ A class to handle CMake module generation

    """
    __slots__ = ("name", "prefix", "template")

    def __init__(self, name=None, prefix=None, template=None):
        self.name     = name
        self.prefix   = prefix
        self.template = template

    def generate_template(self, name, prefix, headers, libraries,
                          path_list=None, interactive=True):
        """Generate a template of CMake module from all information passed.

        :param name:        package name
        :param prefix:      CMake module prefix
        :param header:      header location (used by 'fpath')
        :param libraries:   list of libraries  (used by 'flib')
        :param path_list:   list of the content of the package
                            (default: None)
        :param interactive: enable user interaction
                            (default: True)

        """
        template = generate_template(name, prefix, headers, libraries,
                                     path_list=path_list,
                                     interactive=interactive)
        self.name     = template[0]
        self.prefix   = template[1]
        self.template = template[2]

    def generate_from_directory(self, directory, name, prefix=None,
                                path_list=None, interactive=True):
        """Generate a template of CMake module from the content of directory.

        :param directory:   base directory of the package
        :param name:        package name
        :param prefix:      CMake module prefix
                            (default: None)
        :param path_list:   list of the content of the package
                            (default: None)
        :param interactive: enable user interaction
                            (default: True)

        """
        template = generate_template_from_directory(directory, name,
                                                    prefix=prefix,
                                                    path_list=path_list,
                                                    interactive=interactive)
        self.name     = template[0]
        self.prefix   = template[1]
        self.template = template[2]

    def generate_from_archive(self, archive, name=None, prefix=None,
                              interactive=True):
        """Generate a template of CMake module from an archive.

        :param archive:     archive path of the package
        :param name:        package name
                            (default: None)
        :param prefix:      CMake module prefix
                            (default: None)
        :param interactive: enable user interaction
                            (default: True)

        """
        template = generate_template_from_archive(archive, name=name,
                                                  prefix=prefix,
                                                  interactive=interactive)
        self.name     = template[0]
        self.prefix   = template[1]
        self.template = template[2]

    def write(self, base_dir, prefix=None):
        """Write the CMake module content in the right location.

        This writes the CMake module in::

          base_dir/prefix/share/cmake/self.prefix.lower()/self.prefix.lower()-config.cmake

        :param base_dir: root directory (the package installation DESTDIR)
        :param prefix:   installation prefix (e.g. /usr on Linux)
                         (default: None)

        :return: the path of the generated CMake module

        """
        if self.template is None:
            message = "No CMake module to write"
            qibuild.ui.info(message)
            return None
        module_filename = "{0}-config.cmake".format(self.prefix.lower())
        if prefix is not None:
            module_dir = os.path.join(base_dir, prefix)
        else:
            module_dir = base_dir
        # pep8-ignore: E501
        module_dir  = os.path.join(module_dir, "share", "cmake", self.prefix.lower())
        module_path = os.path.join(module_dir, module_filename)
        qibuild.sh.mkdir(module_dir, recursive=True)
        with open(module_path, "w") as module_file:
            module_file.write(self.template)
        return module_path
