def test_install(qipy_action, tmpdir):
    big_project = qipy_action.add_test_project("big_project")
    dest = tmpdir.join("dest")
    qipy_action("install", "big_project", dest.strpath)
