## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import subprocess

import qisrc.worktree
import qibuild
import qibuild.gdb

def clean_test_dir():
    test_dir = os.path.abspath(os.path.dirname(__file__))
    worktree = qisrc.worktree.open_worktree(test_dir)
    for project in worktree.projects:
        build_dirs = os.listdir(project.path)
        build_dirs = [x for x in build_dirs if x.startswith("build")]
        build_dirs = [os.path.join(project.path, x) for x in build_dirs]
        for build_dir in build_dirs:
            qibuild.sh.rm(build_dir)

def pytest_funcarg__toc(request):
    test_dir = os.path.abspath(os.path.dirname(__file__))
    toc = qibuild.toc.toc_open(test_dir)
    request.addfinalizer(clean_test_dir)
    return toc

def pytest_funcarg__toc_release(request):
    class Namespace:
        pass
    args = Namespace()
    args.build_type = "Release"
    test_dir = os.path.abspath(os.path.dirname(__file__))
    toc = qibuild.toc.toc_open(test_dir, args=args)
    request.addfinalizer(clean_test_dir)
    return toc

def run_gdb(toc):
    debugme_proj = toc.get_project("debugme")
    build_dir = debugme_proj.build_directory
    gdb_ini = os.path.join(build_dir, "gdb.ini")
    with open(gdb_ini, "w") as fp:
        fp.write("""file {binary}
run
bt
q
""".format(binary=os.path.join(build_dir, "sdk/bin/debugme")))
    cmd = ["gdb", "-batch", "-x",  gdb_ini]
    process = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    return process.communicate()


def test_normal_debug(toc):
    proj = toc.get_project("debugme")
    toc.configure_project(proj)
    toc.build_project(proj)
    (out, _)  = run_gdb(toc)
    assert "in foo () at " in out
    assert "main.cpp" in out

def test_split_debug(toc):
    proj = toc.get_project("debugme")
    toc.configure_project(proj)
    toc.build_project(proj)
    qibuild.gdb.split_debug(proj.sdk_directory)
    (out, _) = run_gdb(toc)
    assert "in foo () at " in out
    assert "main.cpp" in out

def test_gdb_release(toc_release):
    proj = toc_release.get_project("debugme")
    toc_release.configure_project(proj)
    toc_release.build_project(proj)
    (out, err) = run_gdb(toc_release)
    assert "No stack" in err
    assert "in foo () at " not in out
