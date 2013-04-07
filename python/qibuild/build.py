## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Low-level build functions

"""

import qisys
from qisys import ui

def make(build_dir, num_jobs=None, target=None):
    """ Launch make from a build dir.
    Launch make -j <num_jobs> in num_jobs is not none

    """
    cmd = ["make"]
    if num_jobs is not None:
        cmd += ["-j%i" % num_jobs]
    if target:
        cmd.append(target)
    qisys.command.call(cmd, cwd=build_dir)


def nmake(build_dir, target=None):
    """ Launch nmake from a build dir.
    For this to work, you may need to be in a Visual
    Studio command prompt, or having run vcvarsall.bar
    """
    cmd = ["nmake"]
    if target:
        cmd.append(target)
    qisys.command.call(cmd, cwd=build_dir)



def msbuild(sln_file, build_type="Debug", target=None, num_jobs=None):
    """ Launch msbuild with correct configuration
    (debug or release), and with correct switch if num_jobs is not None
    """
    msbuild_conf = "/p:Configuration=%s" % build_type

    cmd = ["MSBuild.exe", msbuild_conf]
    cmd += ["/nologo"]
    if num_jobs != None:
        cmd.append("/m:%d" % int(num_jobs))

    if target is not None:
        cmd += ["/target:%s" % target]

    cmd += [sln_file]

    qisys.command.call(cmd)

def num_jobs_to_args(num_jobs, cmake_generator):
    """ Convert a number of jobs to a list of cmake args

    >>> num_jobs_to_args(3, "Unix Makefiles")
    ["-j", "3"]

    >>> num_jobs_to_args(3, "NMake Makefiles"
    Error: -j is not supported for NMake, use Jom

    >>> num_jobs_to_args(3, "Visual Studio")
    Warning: -j is ignored for Visual Studio

    """

    if num_jobs == 1:
        return list()
    if "Unix Makefiles" in cmake_generator or \
       "Ninja" in cmake_generator:
        return ["-j", str(num_jobs)]
    if cmake_generator == "NMake Makefiles":
        mess   = "-j is not supported for %s\n" % cmake_generator
        mess += "On windows, you can use Jom instead to compile "
        mess += "with multiple processors"
        raise Exception(mess)
    if "Visual Studio" in cmake_generator or \
        cmake_generator == "Xcode" or \
        "JOM" in cmake_generator:
        ui.warning("-j is ignored when used with", cmake_generator)
        return list()
    ui.warning("cannot parse -j into a cmake option for generator: %s" % cmake_generator)
    return list()

class BuildFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when building project %s" % self.project.name
