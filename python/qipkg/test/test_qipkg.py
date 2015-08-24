## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qisys.command
import qisys.qixml
import qipkg.package

import pytest

def test_make_package(qipkg_action, qipy_action):
    tmpdir = qipy_action.worktree.tmpdir

    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("b_py")
    c_pkg_proj = qipkg_action.add_test_project("c_pkg")
    qipy_action("bootstrap")

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
    pml = os.path.join(os.path.dirname(__file__), "projects", "empty_uuid", "empty.pml")
    error = qipkg_action("make-package", pml, raises=True)
    assert "uuid" in error

def test_make_package_empty_version(qipkg_action):
    pml = os.path.join(os.path.dirname(__file__), "projects", "empty_version", "empty.pml")
    error = qipkg_action("make-package", pml, raises=True)
    assert "version" in error

def test_breakpad_symbols(qipkg_action):
    dump_syms = qisys.command.find_program("dump_syms", raises=False)
    if not dump_syms:
        return

    a_cpp_proj = qipkg_action.add_test_project("a_cpp")
    pml = os.path.join(a_cpp_proj.path, "a_cpp.pml")

    qipkg_action("configure", "--release", "--with-debug-info", pml)
    qipkg_action("build", pml)
    pkg, symbols_archive = qipkg_action("make-package", "--with-breakpad", pml)
    assert os.path.exists(symbols_archive)

def test_meta(qipkg_action):
    tmpdir = qipkg_action.worktree.tmpdir
    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("d_pkg")
    meta_pkg_proj = qipkg_action.add_test_project("meta_pkg")
    meta_pml = os.path.join(meta_pkg_proj.path, "meta_pkg.mpml")
    qipkg_action("configure", meta_pml)
    qipkg_action("build", meta_pml)
    pkgs = qipkg_action("make-package", meta_pml)
    expected_paths = [
            "a-0.1.pkg",
            "d-0.1.pkg"
    ]
    actual_paths = [os.path.basename(x) for x in pkgs]
    assert actual_paths == expected_paths


def test_no_worktree_pure_pml(tmpdir, monkeypatch):
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
    # pylint:disable-msg=E1101
    with pytest.raises(Exception) as error:
        package = qisys.script.run_action("qipkg.actions.make_package", [pml_path.strpath])
    assert "not in a worktree" in error.value.message

def test_translations(qipkg_action, tmpdir):
    tr_project = qipkg_action.add_test_project("tr_project")
    pml_path = os.path.join(tr_project.path, "tr.pml")
    package = qipkg_action("make-package", pml_path)
    dest = tmpdir.mkdir("dest")
    qipkg_action.chdir(dest)
    qipkg_action("extract-package", package)
    assert dest.join("tr-0.1", "translations", "tr_fr_FR.qm").check(file=True)

def test_validate_package(qipkg_action):
    pkg_path = os.path.join(os.path.dirname(__file__), "projects", "python_services.pkg")
    qipkg_action("validate_package", pkg_path)

def test_validate_package_exception(qipkg_action):
    pkg_path = os.path.join(os.path.dirname(__file__), "projects", "invalid_package.pkg")
    error = qipkg_action("validate_package", pkg_path, raises=True)
    assert error == "Given package does not satisfy default package requirements"

def test_release_package(qipkg_action, tmpdir):
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
    assert(services[0].attrib["execStart"] == "/usr/bin/python2.7 lib/my_service.pyc")
    assert(services[1].attrib["execStart"] == "/usr/bin/python2.7 lib/my_service.pyc '127.0.0.1'")
    # it was already pointing to a *.pyc file, nothing should have changed
    assert(services[2].attrib["execStart"] == "/usr/bin/python2.7 lib/my_service.pyc")
    # it is not pointing to a file of the package, nothing should have changed
    assert(services[3].attrib["execStart"] == "/usr/bin/python2.7 tata.py")
