import os

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
            "python",
            "lib/libfoo.so",
            "lib/python2.7/site-packages/b.py",
            "c_behavior/behavior.xar",
    ]
    for path in expected_paths:
        full_path = tmpdir.join("c-0.1", path)
        assert full_path.check(file=True)

