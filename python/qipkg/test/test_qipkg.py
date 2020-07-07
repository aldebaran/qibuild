#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiPkg """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys
import mock
import pytest
import platform

import qipkg.builder
import qipkg.package
import qisys.qixml
import qisys.command
from qisys.qixml import etree
from qisys.test.conftest import record_messages
from qibuild.test.test_qibuild_deploy import get_ssh_url

TARGET = "{}-{}".format(platform.system().lower(),
                        platform.processor().lower())


def test_ls_package(qipkg_action, record_messages):
    """ Test Ls Package """
    pkg_path = os.path.join(os.path.dirname(__file__), "projects", "python_services.pkg")
    qipkg_action("ls-package", pkg_path)
    assert record_messages.find("lib/my_service.py")
    assert record_messages.find("manifest.xml")


def test_make_package(qipkg_action, qipy_action):
    """ Test Make Package """
    tmpdir = qipy_action.worktree.tmpdir
    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("b_py")
    c_pkg_proj = qipkg_action.add_test_project("c_pkg")
    # ipython 5 is the last version compatible with Python 2.7
    qipy_action("bootstrap", "pip", "virtualenv", "ipython<=5")
    pml = os.path.join(c_pkg_proj.path, "c_pkg.pml")
    qipkg_action("configure", pml)
    qipkg_action("build", pml)
    pkg = qipkg_action("make-package", pml)
    qipkg_action("extract-package", pkg)
    expected_paths = [
        "manifest.xml",
        "lib/libfoo.so",
        "lib/python2.7/site-packages/b.py",
        "c_behavior/behavior.xar",
    ]
    for path in expected_paths:
        full_path = tmpdir.join("c-0.1", path)
        assert full_path.check(file=True)


def test_make_package_empty_uuid(qipkg_action):
    """ Test Package Empty UUID """
    pml = os.path.join(os.path.dirname(__file__), "projects", "empty_uuid", "empty.pml")
    error = qipkg_action("make-package", pml, raises=True)
    assert "uuid" in error


def test_make_package_empty_version(qipkg_action):
    """ Test Make Package Empty Version """
    pml = os.path.join(os.path.dirname(__file__), "projects", "empty_version", "empty.pml")
    error = qipkg_action("make-package", pml, raises=True)
    assert "version" in error


def test_breakpad_symbols(qipkg_action):
    """ Test Breakpad Symbols """
    dump_syms = qisys.command.find_program("dump_syms", raises=False)
    if not dump_syms:
        return
    a_cpp_proj = qipkg_action.add_test_project("a_cpp")
    pml = os.path.join(a_cpp_proj.path, "a_cpp.pml")
    qipkg_action("configure", "--release", "--with-debug-info", pml)
    qipkg_action("build", pml)
    _pkg, symbols_archive = qipkg_action("make-package", "--with-breakpad", pml)
    assert os.path.exists(symbols_archive)


def test_meta(qipkg_action):
    """ Test Meta """
    _tmpdir = qipkg_action.worktree.tmpdir
    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("d_pkg")
    meta_pkg_proj = qipkg_action.add_test_project("meta_pkg")
    meta_pml = os.path.join(meta_pkg_proj.path, "meta_pkg.mpml")
    qipkg_action("configure", meta_pml)
    qipkg_action("build", meta_pml)
    pkgs = qipkg_action("make-package", meta_pml)
    expected_paths = [
        "a-0.1-{}.pkg".format(TARGET),
        "d-0.1-{}.pkg".format(TARGET)
    ]
    actual_paths = [os.path.basename(x) for x in pkgs]
    assert actual_paths == expected_paths


def test_no_worktree_pure_pml(tmpdir, monkeypatch):
    """ Test No Worktree Pure Pml """
    project = tmpdir.mkdir("project")
    project.ensure("behavior_1", "behavior.xar", file=True)
    manifest_path = project.join("manifest.xml")
    manifest_path.write("""
<package version="0.1" uuid="fooproject">
  <names>
    <name lang="en_US">fooproject</name>
  </names>
  <supportedLanguages>
    <language>en_US</language>
  </supportedLanguages>
  <requirements>
    <naoqiRequirement minVersion="1.22"/>
    <robotRequirement model="NAO"/>
  </requirements>
</package>
""")
    pml_path = project.join("project.pml")
    pml_path.write("""
<Package name="project">

    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>

</Package>
""")
    monkeypatch.chdir(tmpdir)
    package = qisys.script.run_action("qipkg.actions.make_package", [pml_path.strpath])
    dest = tmpdir.mkdir("dest")
    monkeypatch.chdir(dest)
    qisys.script.run_action("qipkg.actions.extract_package", [package])
    assert dest.join("fooproject-0.1", "manifest.xml").check(file=True)
    assert dest.join("fooproject-0.1", "behavior_1", "behavior.xar").check(file=True)


def test_no_worktre_bad_pml(tmpdir, monkeypatch):
    """ Test No Worktree Bad Pml """
    project = tmpdir.mkdir("project")
    manifest_path = project.join("manifest.xml")
    manifest_path.write("""
<package version="0.1" uuid="fooproject">
  <names>
    <name lang="en_US">fooproject</name>
  </names>
  <supportedLanguages>
    <language>en_US</language>
  </supportedLanguages>
  <requirements>
    <naoqiRequirement minVersion="1.22"/>
    <robotRequirement model="NAO"/>
  </requirements>
</package>
""")
    pml_path = project.join("project.pml")
    pml_path.write("""
<Package name="project">
    <qibuild name="foo" />
</Package>
""")
    monkeypatch.chdir(tmpdir)
    with pytest.raises(Exception) as error:
        _package = qisys.script.run_action("qipkg.actions.make_package", [pml_path.strpath])
    assert "not in a worktree" in str(error)


def test_translations(qipkg_action, tmpdir):
    """ Test Translation """
    tr_project = qipkg_action.add_test_project("tr_project")
    pml_path = os.path.join(tr_project.path, "tr.pml")
    package = qipkg_action("make-package", pml_path)
    dest = tmpdir.mkdir("dest")
    qipkg_action.chdir(dest)
    qipkg_action("extract-package", package)
    assert dest.join("tr-0.1", "translations", "tr_fr_FR.qm").check(file=True)


def test_validate_package(qipkg_action):
    """ Test Validate Package """
    pkg_path = os.path.join(os.path.dirname(__file__), "projects", "python_services.pkg")
    qipkg_action("validate_package", pkg_path)


def test_validate_package_exception(qipkg_action):
    """ Test Validate Package Extension """
    pkg_path = os.path.join(os.path.dirname(__file__), "projects", "invalid_package.pkg")
    error = qipkg_action("validate_package", pkg_path, raises=True)
    assert error == "Given package does not satisfy default package requirements"


def test_release_package(qipkg_action, tmpdir):
    """ Test Release Package """
    pkg_path = os.path.join(os.path.dirname(__file__), "projects", "python_services.pkg")
    output_path = tmpdir.join("output.pkg")
    qipkg_action("release-package", pkg_path, "--output", str(output_path))
    dest = tmpdir.mkdir("dest")
    qipkg_action.chdir(dest)
    qipkg_action("extract-package", str(output_path))
    package = dest.join("python_services-0.0.2")
    assert package.join("lib", "my_service.pyc").check(file=True)
    assert package.join("lib", "my_service.py").check(file=False)
    tree = qisys.qixml.read(str(package.join("manifest.xml")))
    services = tree.getroot().findall("services/service")
    assert services[0].attrib["execStart"] == "/usr/bin/python2.7 lib/my_service.pyc"
    assert services[1].attrib["execStart"] == "/usr/bin/python2.7 lib/my_service.pyc '127.0.0.1'"
    # it was already pointing to a *.pyc file, nothing should have changed
    assert services[2].attrib["execStart"] == "/usr/bin/python2.7 lib/my_service.pyc"
    # it is not pointing to a file of the package, nothing should have changed
    assert services[3].attrib["execStart"] == "/usr/bin/python2.7 tata.py"


def test_qipkg_in_wrong_directory(qipkg_action):
    """ Test QiPkg In Wrong Directory """
    error = qipkg_action("make-package", "foo.pml", raises=True)
    assert "foo.pml" in error


def test_qipkg_no_such_project(qipkg_action, tmpdir):
    """ Test QiPkg No Such Project """
    d_project = qipkg_action.add_test_project("d_pkg")
    pml_path = os.path.join(d_project.path, "d_pkg.pml")
    root = qisys.qixml.read(pml_path).getroot()
    elem = etree.SubElement(root, "qipython")
    elem.set("name", "foo")
    qisys.qixml.write(root, pml_path)
    error = qipkg_action("make-package", pml_path, raises=True)
    assert "No such python project: foo" in error
    assert pml_path in error


def test_bump_version(qipkg_action):
    """ Test Bump Version """
    d_proj = qipkg_action.add_test_project("d_pkg")
    manifest_xml = os.path.join(d_proj.path, "manifest.xml")
    name = qipkg.builder.pkg_name(manifest_xml)
    assert name == "d-0.1"
    qipkg_action("bump-version", manifest_xml)
    name = qipkg.builder.pkg_name(manifest_xml)
    assert name == "d-0.2"
    qipkg_action("bump-version", manifest_xml, "2.0")
    name = qipkg.builder.pkg_name(manifest_xml)
    assert name == "d-2.0"


def test_install(qipkg_action, tmpdir):
    """ Test Install """
    d_proj = qipkg_action.add_test_project("d_pkg")
    pml_path = os.path.join(d_proj.path, "d_pkg.pml")
    d_package = qipkg_action("make-package", pml_path)
    _url = get_ssh_url(tmpdir)
    qipkg_action("install", pml_path, tmpdir.strpath)
    assert tmpdir.join("manifest.xml").check(file=True)


def test_deploy(qipkg_action, tmpdir):
    """ Test Deploy """
    d_proj = qipkg_action.add_test_project("d_pkg")
    pml_path = os.path.join(d_proj.path, "d_pkg.pml")
    d_package = qipkg_action("make-package", pml_path)
    url = get_ssh_url(tmpdir)
    qipkg_action("deploy", pml_path, "--url", url)
    assert tmpdir.join("manifest.xml").check(file=True)


def test_deploy_package_no_qi(qipkg_action, tmpdir, record_messages):
    """ Test Deploy Package """
    d_proj = qipkg_action.add_test_project("d_pkg")
    pml_path = os.path.join(d_proj.path, "d_pkg.pml")
    d_package = qipkg_action("make-package", pml_path)
    url = get_ssh_url(tmpdir)
    record_messages.reset()
    qipkg_action("deploy-package", d_package, "--url", url)
    try:
        qipkg_action("deploy-package", d_package, "--url", url)
    except ImportError:
        assert record_messages("Unable to install pkg, please install qi from pip and retry.")


def test_deploy_package(qipkg_action, tmpdir, record_messages):
    """ Test Deploy Package """
    try:
        import qi
        d_proj = qipkg_action.add_test_project("d_pkg")
        pml_path = os.path.join(d_proj.path, "d_pkg.pml")
        d_package = qipkg_action("make-package", pml_path)
        url = get_ssh_url(tmpdir)
        parsed = qisys.remote.URL(url)
        username = parsed.user
        fake_qi = mock.Mock()
        fake_qi.Application = mock.Mock()
        fake_app = mock.Mock()
        fake_qi.Application.return_value = fake_app
        session = fake_qi.Session()
        mock_connect = session.connect
        fake_pm = mock.Mock()
        session.service.return_value = fake_pm
        remove_mock = fake_pm.removePkg
        install_mock = fake_pm.install
        install_mock.return_value = True
        sys.modules["qi"] = fake_qi
        record_messages.reset()
        qipkg_action("deploy-package", d_package, "--url", url)
        assert mock_connect.call_args_list == [mock.call("tcp://localhost:9559")]
        assert session.service.call_args_list == [mock.call("PackageManager")]
        assert remove_mock.call_args_list == [mock.call("d")]
        assert install_mock.call_args_list == [mock.call("/home/%s/d-0.1.pkg" % username)]
        assert record_messages.find("PackageManager returned: True")
        del sys.modules["qi"]
    except ImportError:
        pass


def test_deploy_package_from_pml_no_qi(qipkg_action, tmpdir, record_messages):
    """ Test Deploy Package From Pml """
    d_proj = qipkg_action.add_test_project("d_pkg")
    pml_path = os.path.join(d_proj.path, "d_pkg.pml")
    url = get_ssh_url(tmpdir)
    record_messages.reset()
    try:
        qipkg_action("deploy-package", pml_path, "--url", url)
    except ImportError:
        assert record_messages("Unable to install pkg, please install qi from pip and retry.")


def test_deploy_package_from_pml(qipkg_action, tmpdir, record_messages):
    """ Test Deploy Package From Pml """
    try:
        import qi
        d_proj = qipkg_action.add_test_project("d_pkg")
        pml_path = os.path.join(d_proj.path, "d_pkg.pml")
        url = get_ssh_url(tmpdir)
        parsed = qisys.remote.URL(url)
        username = parsed.user
        fake_qi = mock.Mock()
        fake_qi.Application = mock.Mock()
        fake_app = mock.Mock()
        fake_qi.Application.return_value = fake_app
        session = fake_qi.Session()
        mock_connect = session.connect
        fake_pm = mock.Mock()
        session.service.return_value = fake_pm
        remove_mock = fake_pm.removePkg
        install_mock = fake_pm.install
        install_mock.return_value = True
        sys.modules["qi"] = fake_qi
        record_messages.reset()
        qipkg_action("deploy-package", pml_path, "--url", url)
        assert mock_connect.call_args_list == [mock.call("tcp://localhost:9559")]
        assert session.service.call_args_list == [mock.call("PackageManager")]
        assert remove_mock.call_args_list == [mock.call("d")]
        assert install_mock.call_args_list == [mock.call("/home/%s/d-0.1.pkg" % username)]
        assert record_messages.find("PackageManager returned: True")
        del sys.modules["qi"]
    except ImportError:
        pass
