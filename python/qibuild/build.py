#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Low-level build functions """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys


def make(build_dir, num_jobs=None, target=None):
    """
    Launch make from a build dir.
    Launch make -j <num_jobs> in num_jobs is not none
    """
    cmd = ["make"]
    if num_jobs is not None:
        cmd += ["-j%i" % num_jobs]
    if target:
        cmd.append(target)
    qisys.command.call(cmd, cwd=build_dir)


def nmake(build_dir, target=None):
    """
    Launch nmake from a build dir.
    For this to work, you may need to be in a Visual
    Studio command prompt, or having run vcvarsall.bar
    """
    cmd = ["nmake"]
    if target:
        cmd.append(target)
    qisys.command.call(cmd, cwd=build_dir)


def msbuild(sln_file, build_type="Debug", target=None, num_jobs=None):
    """
    Launch msbuild with correct configuration (debug or release),
    and with correct switch if num_jobs is not None.
    """
    msbuild_conf = "/p:Configuration=%s" % build_type
    cmd = ["MSBuild.exe", msbuild_conf]
    cmd += ["/nologo"]
    if num_jobs is not None:
        cmd.append("/m:%d" % int(num_jobs))
    if target is not None:
        cmd += ["/target:%s" % target]
    cmd += [sln_file]
    qisys.command.call(cmd)


class BuildFailed(Exception):
    """ BuildFailed Exception """

    def __init__(self, project):
        """ BuildFailed Init """
        super(BuildFailed, self).__init__()
        self.project = project

    def __str__(self):
        """ String Representation """
        return "Error occurred when building project %s" % self.project.name


class ConfigureFailed(Exception):
    """ ConfigureFailed Exception """

    def __init__(self, project, exception=None):
        """ ConfigureFailed Init """
        super(ConfigureFailed, self).__init__()
        self.project = project
        self.exception = exception

    def __str__(self):
        """ String Representation """
        mess = "Error occurred when configuring project %s" % self.project.name
        returncode = self.exception.returncode
        if returncode < 0:
            mess += " (%s)" % qisys.command.str_from_signal(-returncode)
        return mess
