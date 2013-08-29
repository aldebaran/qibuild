
def test_run(build_worktree):
    testme = build_worktree.add_test_project("testme")
    testme.configure()
    testme.build()
    ok = testme.run_tests()
    assert not ok

