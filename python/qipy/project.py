# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import os

import qisys.sh


class PythonProject(object):  # pylint: disable=too-many-instance-attributes
    """ Collections of scripts, modules and packages """

    def __init__(self, worktree, src, name):
        self.worktree = worktree
        self.src = src
        self.path = os.path.join(worktree.root, src)
        self.name = name
        self.scripts = list()
        self.modules = list()
        self.packages = list()
        self.setup_with_distutils = False

    @property
    def python_path(self):
        """ List of path to add to $PYTHONPATH to use this project """
        res = list()
        for module_package in self.modules + self.packages:
            src = module_package.src
            to_add = os.path.join(self.worktree.root, self.src, src)
            to_add = qisys.sh.to_native_path(to_add)
            if to_add not in res:
                res.append(to_add)
        return res

    def install(self, dest):  # pylint: disable=too-many-locals
        """ Install scripts, modules and packages to the given destination """
        empty = (not self.setup_with_distutils) and \
            (not self.scripts) and \
            (not self.modules) and \
            (not self.packages)
        if empty:
            mess = """
Could not find anything to install.
Either write a setup.py file and use
    <setup with_distutils="true" />
Or specify at least some scripts, modules or packages
in the qiproject.xml file
"""
            raise Exception(mess)
        if self.setup_with_distutils:
            python = self.worktree.python
            if not os.path.exists(python):
                mess = "Python executable not found in virtualenv\n"
                mess += "Try running `qipy bootstrap`"
                raise Exception(mess)
            cmd = [python, "setup.py", "install", "--root", dest, "--prefix=."]
            qisys.command.call(cmd, cwd=self.path)
            return

        for script in self.scripts:
            script_dest = os.path.join(dest, "bin")
            qisys.sh.mkdir(script_dest, recursive=True)
            script_src = os.path.join(self.path, script.src)
            qisys.sh.install(script_src, script_dest)

        site_packages = os.path.join(dest, "lib", "python2.7", "site-packages")
        qisys.sh.mkdir(site_packages, recursive=True)

        for module in self.modules:
            full_src = os.path.join(self.path, module.src, module.name + ".py")
            qisys.sh.install(full_src, site_packages)

        for package in self.packages:
            package_contents = self.walk_package(package)
            for filename in package_contents:
                dirname = os.path.dirname(filename)
                full_src = os.path.join(self.path, package.src, package.name, filename)
                to_make = os.path.join(site_packages, package.name, dirname)
                qisys.sh.mkdir(to_make, recursive=True)
                qisys.sh.install(full_src, to_make)

    def walk_package(self, package):
        """ Returns all the .py files in the given package"""
        res = list()
        full_package_path = os.path.join(self.path, package.src, package.name)
        for root, __directories, filenames in os.walk(full_package_path):  # pylint: disable=unused-variable
            init_py = os.path.join(root, "__init__.py")
            if not os.path.exists(init_py):
                continue
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                full_path = os.path.join(root, filename)
                rel_src = os.path.relpath(full_path, full_package_path)
                res.append(rel_src)
        res.sort()
        return res

    @property
    def setup_dot_py(self):
        return os.path.join(self.path, "setup.py")

    def __repr__(self):
        return "<%s in %s>" % (self.name, self.src)


class Module(object):
    def __init__(self, name, src):
        self.name = name
        self.src = src
        self.qimodule = False


class Package(object):
    def __init__(self, name, src):
        self.name = name
        self.src = src
        self.qimodule = False


class Script(object):
    def __init__(self, src):
        self.src = src
