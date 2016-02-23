## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for qibuild with coverage option

"""

import os

import qisys.command
import qisys.qixml
import qibuild.gcov

from qisys.test.conftest import only_linux
from qibuild.test.conftest import TestBuildWorkTree
from qitest.test.conftest import qitest_action

def check_cov_xml(xml_path):
    """ Check that generated XML file is correct

    """
    tree = qisys.qixml.read(xml_path)
    root = tree.getroot()
    foo_elem = root.find("packages/package/classes/class[@filename='foo.cpp']")
    assert foo_elem is not None
    # line 8 should have 0 hits:
    line_8_elem = foo_elem.find("lines/line[@number='8']")
    assert line_8_elem.get("hits") == "0"
    # line 5 should have 1 hit:
    line_5_elem = foo_elem.find("lines/line[@number='5']")
    assert line_5_elem.get("hits") == "1"

# Even though clang supports the --cov flag, gcovr does not seem
# to work on mac
@only_linux
def test_generate_reports(tmpdir, qibuild_action, qitest_action):
    gcovr = qisys.command.find_program("gcovr", raises=False)
    if not gcovr:
        return
    proj = qibuild_action.add_test_project("coverme")
    qibuild_action("configure", "coverme", "--coverage")
    qibuild_action("make", "coverme")
    qitest_action("run", "coverme")
    qibuild.gcov.generate_coverage_reports(proj,
                                           exclude_patterns=list())
    expected_path_xml = os.path.join(proj.sdk_directory,
                                     "coverage-results",
                                     proj.name + ".xml")
    expected_path_html = os.path.join(proj.sdk_directory,
                                       "coverage-results",
                                       proj.name + ".html")
    assert os.path.exists(expected_path_xml)
    assert os.path.exists(expected_path_html)
    check_cov_xml(expected_path_xml)

    # Now test with an other output dir
    output_dir = tmpdir.join("out").strpath
    qibuild.gcov.generate_coverage_reports(proj, output_dir=output_dir,
                                           exclude_patterns=list())

    expected_path_xml = os.path.join(output_dir, proj.name + ".xml")
    expected_path_html = os.path.join(output_dir, proj.name + ".html")
    assert os.path.exists(expected_path_xml)
    assert os.path.exists(expected_path_html)
    check_cov_xml(expected_path_xml)

@only_linux
def test_custom_build_prefix(qibuild_action, qitest_action):
    build_worktree = TestBuildWorkTree()
    qibuild_action.add_test_project("coverme")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.local.build.prefix = "prefix"
    qibuild_cfg.write_local_config(build_worktree.qibuild_xml)
    qibuild_action("configure", "coverme", "--coverage")
    qibuild_action("make", "coverme")
    qitest_action("run", "coverme", "--coverage", "--cov-exclude=NONE")
    # re-init a TestBuildWorkTree so that local setting are read
    build_worktree = TestBuildWorkTree()
    coverme_project = build_worktree.get_build_project("coverme")
    xml_path = os.path.join(coverme_project.sdk_directory,
                            "coverage-results", "coverme.xml")
    check_cov_xml(xml_path)
