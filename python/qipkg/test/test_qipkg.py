import os

import qisys.command

def test_make_package(qipkg_action, qipy_action):
    tmpdir = qipy_action.worktree.tmpdir

    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("b_py")
    c_pkg_proj = qipkg_action.add_test_project("c_pkg")
    qipy_action("bootstrap")

    pml = os.path.join(c_pkg_proj.path, "c_pkg.pml")
    qipkg_action("configure", pml)
    qipkg_action("build", pml)
    pkgs = qipkg_action("make-package", pml)
    assert len(pkgs) == 1
    pkg = pkgs[0]

    qipkg_action("extract-package", pkg)

    expected_paths = [
            "manifest.xml",
            "python",
            "lib/libfoo.so",
            "lib/python2.7/site-packages/b.py",
            "c_behavior/behavior.xar",
    ]
    for path in expected_paths:
        full_path = tmpdir.join("c-0.1", path)
        assert full_path.check(file=True)

def test_breakpad_symbols(qipkg_action):
    dump_syms = qisys.command.find_program("dump_syms", raises=False)
    if not dump_syms:
        return

    a_cpp_proj = qipkg_action.add_test_project("a_cpp")
    pml = os.path.join(a_cpp_proj.path, "a_cpp.pml")

    qipkg_action("configure", "--release", "--with-debug-info", pml)
    qipkg_action("build", "--release", pml)
    pkg, symbols_archive = qipkg_action("make-package", "--with-breakpad", "--release", pml)
    assert os.path.exists(symbols_archive)

def test_meta(qipkg_action):
    tmpdir = qipkg_action.worktree.tmpdir
    qipkg_action.add_test_project("a_cpp")
    qipkg_action.add_test_project("d_pkg")
    meta_pkg_proj = qipkg_action.add_test_project("meta_pkg")
    meta_pml = os.path.join(meta_pkg_proj.path, "meta_pkg.mpml")
    qipkg_action("configure", meta_pml)
    qipkg_action("build", meta_pml)
    pkg = qipkg_action("make-package", meta_pml)
    qipkg_action("extract-package", pkg)

    expected_paths = [
            "a-0.1.pkg",
            "d-0.1.pkg"
    ]
    for path in expected_paths:
        full_path = tmpdir.join("meta-0.1", path)
        assert full_path.check(file=True)
