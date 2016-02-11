## Copyright (c) 2009-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from __future__ import print_function

import os
import multiprocessing

from invoke import task, run

def find_modules():
    res = list()
    for entry in sorted(os.listdir(os.getcwd())):
        init_py = os.path.join(entry, "__init__.py")
        if os.path.exists(init_py):
            res.append(entry)
        if entry.endswith(".py"):
            res.append(entry)
    res.remove("tasks.py")
    return res

@task
def pylint(errors_only=False):
    modules = find_modules()
    message = "Running pylint"
    cmd = "pylint " + " ".join(modules)
    cmd += " --rcfile pylint.rc"
    if errors_only:
        cmd += " --errors-only"
        message += " (errors only)"
    print(message)
    run(cmd)

@task
def test(coverage=False):
    cmd = "py.test"
    cmd += " -n%i" % multiprocessing.cpu_count()
    if coverage:
        cmd += " --cov=. --cov-report=html"
    pytest_opts = os.environ.get("PYTEST_OPTS")
    if pytest_opts:
        cmd += " " + pytest_opts
    print("Running tests with py.test ...")
    run(cmd)

@task
def install():
    cmd = "pip install -r ../requirements.txt"
    print("Installing dependencies with pip ...")
    run(cmd)

@task
def release(sign=True):
    run("cd .. ; rm -fr dist")
    run("cd .. ; python setup.py sdist bdist_wheel")
    cmd = "cd .. ; twine upload dist/*"
    if sign:
        cmd += " --sign"
    run(cmd)
