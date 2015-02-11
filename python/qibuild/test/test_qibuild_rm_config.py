import qibuild.config

def test_remove(qibuild_action):
    qibuild_action("add-config", "foo", "--toolchain", "foo")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    assert qibuild_cfg.configs.get("foo")
    qibuild_action("rm-config", "foo")
    qibuild_cfg2 = qibuild.config.QiBuildConfig()
    qibuild_cfg2.read()
    assert qibuild_cfg2.configs.get("foo") is None
