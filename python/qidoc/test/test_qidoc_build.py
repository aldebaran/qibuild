def test_simple_build(qidoc_action):
    qidoc_action.add_test_project("libqi")
    qidoc_action("build", "qi-api")
