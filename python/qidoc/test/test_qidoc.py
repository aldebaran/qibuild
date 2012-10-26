## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import pytest

import qisys
import qisys.script


def check_tools():
    """ Check if all the tools are installed.

    If not return a string describing what is missing

    """
    mess = ""
    executables = dict()
    try:
        import pyparsing
    except ImportError:
        mess += "please install pyparsing for doxylink to work"

    for name in ["sphinx-build", "sphinx-build2",
                 "doxygen", "dot", "linkchecker"]:
        executables[name] = qisys.command.find_program(name)

    if "sphinx-build" not in executables and "sphinx-build2" not in executables:
        mess += "sphinx-build not found"

    if "doxygen" not in executables:
        mess += "doxygen not found"

    if "dot" not in executables:
        mess += "graphviz not installed, dot executable not found"

    if "linkchecker" not in executables:
        mess += "linkchecker is not installed"

    if mess:
        print mess
        return False
    else:
        return True


def pytest_funcarg__src_doc(request):
    this_dir = os.path.dirname(__file__)
    src_dir = os.path.join(this_dir, "in")
    def clean():
        build_doc = os.path.join(src_dir, "build-doc")
        qisys.sh.rm(build_doc)
    request.addfinalizer(clean)
    return src_dir

@pytest.mark.slow()
def test_qidoc(src_doc):
    if not check_tools():
        return
    args = ["-w", src_doc]
    qisys.script.run_action("qidoc.actions.build", args)
    # XXX: should check for broken links in build-doc
