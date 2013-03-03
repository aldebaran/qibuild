from qisys import ui
import qisys.script
import qisys.sh

def test_option_checking(qisrc_action):
    qisrc_action("init")
    error = qisrc_action("manifest", "--add",  raises=True)
    assert "when using --add" in error
    error = qisrc_action("manifest", "--add",  "foo", raises=True)
    assert "when using --add" in error
    error = qisrc_action("manifest", "--remove",  raises=True)
    assert "when using --remove" in error

def test_list_no_groups(qisrc_action, git_server, record_messages):
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)
    qisrc_action("manifest", "--list")
    assert ui.find_message(manifest_url)
    assert not ui.find_message("groups")

def test_list_groups(qisrc_action, git_server, record_messages):
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    qisrc_action("init", manifest_url, "--group", "mygroup")
    qisrc_action("manifest", "--list")
    assert ui.find_message(manifest_url)
    assert ui.find_message("groups")
    assert ui.find_message("mygroup")

def test_add(qisrc_action, git_server):
    qisrc_action("init")
    manifest_url = git_server.manifest_url
    qisrc_action("manifest", "--add", "mymanifest", manifest_url)
    assert "mymanifest" in qisrc_action.git_worktree.manifests

def test_remove_add(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)
    qisrc_action("manifest", "--remove", "default")
    assert not qisrc_action.git_worktree.manifests
    qisrc_action("manifest", "--add", "default", manifest_url)
    assert "default" in qisrc_action.git_worktree.manifests

def test_reconfigure(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("c")
    qisrc_action("init", manifest_url)
    assert len(qisrc_action.git_worktree.git_projects) == 3
    qisrc_action("manifest", "default", "-g", "mygroup")
    assert len(qisrc_action.git_worktree.git_projects) == 2
