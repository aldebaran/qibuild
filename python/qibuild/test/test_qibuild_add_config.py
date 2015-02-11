import qibuild.config

def test_add_config(qibuild_action):
    qibuild_action("add-config", "foo",
                   "--toolchain", "foo",
                   "--profile", "bar", "--profile", "baz",
                   "--cmake-generator", "Ninja",
                   "--ide", "QtCreator")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    foo_cfg = qibuild_cfg.configs.get("foo")
    assert foo_cfg.name == "foo"
    assert foo_cfg.toolchain == "foo"
    assert foo_cfg.cmake.generator == "Ninja"
    assert foo_cfg.profiles == ["bar", "baz"]
    assert foo_cfg.ide == "QtCreator"

def test_set_default_config(qibuild_action, build_worktree):
    qibuild_action("add-config", "foo", "--default")
    assert build_worktree.default_config == "foo"
