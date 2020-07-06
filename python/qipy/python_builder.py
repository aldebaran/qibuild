#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qipy.venv
import qisys.remote
import qisys.command
from qisys import ui
from qisys.abstractbuilder import AbstractBuilder
from qibuild.project import write_qi_path_conf


class PythonBuilder(AbstractBuilder):
    """ Managing python projects """

    def __init__(self, python_worktree, build_worktree=None):
        """ PythonBuilder Init """
        super(PythonBuilder, self).__init__(self.__class__.__name__)
        self.python_worktree = python_worktree
        self.build_worktree = build_worktree
        self.projects = list()

    @property
    def config(self):
        """ Config """
        return self.python_worktree.config

    def bootstrap(self, remote_packages=None, site_packages=True,
                  python_executable=None, env=None):
        """ Configure the virtualenv so that importing any Python module works """
        ok = qipy.venv.configure_virtualenv(self.config,
                                            self.python_worktree,
                                            build_worktree=self.build_worktree,
                                            remote_packages=remote_packages,
                                            site_packages=site_packages,
                                            python_executable=python_executable,
                                            env=env)
        qi_path_sdk_dirs = [p.sdk_directory for p in self.build_worktree.build_projects]
        write_qi_path_conf(self.python_worktree.venv_path, qi_path_sdk_dirs)
        return ok

    def configure(self, *args, **kwargs):
        "Configure, no -op"
        pass

    def build(self, *args, **kwargs):
        "Build, no -op"
        pass

    def install(self, dest, *args, **kwargs):
        """
        Just copy the Python scripts, modules and packages.
        If there are extensions written in CMake, they will be
        installed by the CMakeBuilder.
        """
        if not self.projects:
            return
        n = len(self.projects)
        for i, project in enumerate(self.projects):
            ui.info_count(i, n, ui.green, "Installing",
                          ui.reset, ui.blue, project.name)
            project.install(dest)
        # Also install a python wrapper so that everything goes smoothly
        to_write = """\
#!/bin/bash
SDK_DIR="$(dirname "$(readlink -f $0 2>/dev/null)")"
export LD_LIBRARY_PATH="${SDK_DIR}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PYTHONPATH="${SDK_DIR}/lib/python2.7/site-packages${PYTHONPATH:+:$PYTHONPATH}"
exec python "$@"
"""
        python_wrapper = os.path.join(dest, "python")
        with open(python_wrapper, "w") as fp:
            fp.write(to_write)
        os.chmod(python_wrapper, 0o755)

    def deploy(self, url):
        """ Deploy scripts, modules and packages to the remote url """
        with qisys.sh.TempDir() as tmp:
            self.install(tmp)
            qisys.remote.deploy(tmp, url)
