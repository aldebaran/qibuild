from qibuild.test.conftest import *

import qibuild.find

import pytest

@pytest.fixture
def compiled_tests(build_worktree):
    testme_proj = build_worktree.add_test_project("testme")
    testme_proj.configure()
    testme_proj.build()

    tests = list()
    paths = [testme_proj.sdk_directory]
    for name in ["ok", "fail", "segfault", "timeout"]:
        test = {
            "name" : name,
            "cmd" : [qibuild.find.find_bin(paths, name)],
        }
        if name == "timeout":
            test["timeout"] = 1
        tests.append(test)
    return tests

