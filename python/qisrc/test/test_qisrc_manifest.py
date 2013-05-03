import qisrc.manifest
from qisrc.test.conftest import TestGitWorkTree

def test_option_checking(qisrc_action):
    error = qisrc_action("manifest", "--add",  raises=True)
    assert "when using --add" in error
    error = qisrc_action("manifest", "--add",  "foo", raises=True)
    assert "when using --add" in error
    error = qisrc_action("manifest", "--remove",  raises=True)
    assert "when using --remove" in error
    error = qisrc_action("manifest", "--check", raises=True)
    assert "when using --check" in error

def test_list_no_groups(qisrc_action, git_server, record_messages):
    manifest_url = git_server.manifest_url
    qisrc_action("manifest", "--add", "default", manifest_url)
    qisrc_action("manifest", "--list")
    assert record_messages.find(manifest_url)
    assert not record_messages.find("groups:")

def test_list_groups(qisrc_action, git_server, record_messages):
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    qisrc_action("manifest", "--add", "--group", "mygroup",
                 "default", manifest_url)
    qisrc_action("manifest", "--list")
    assert record_messages.find(manifest_url)
    assert record_messages.find("groups")
    assert record_messages.find("mygroup")

def test_add(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    qisrc_action("manifest", "--add", "mymanifest", manifest_url)
    git_worktree = TestGitWorkTree()
    assert "mymanifest" in git_worktree.manifests

def test_remove_add(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    qisrc_action("manifest", "--add", "default", manifest_url)
    qisrc_action("manifest", "--remove", "default")
    git_worktree = TestGitWorkTree()
    assert not git_worktree.manifests
    qisrc_action("manifest", "--add", "default", manifest_url)
    git_worktree = TestGitWorkTree()
    assert "default" in git_worktree.manifests

def test_reconfigure(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("c")
    qisrc_action("manifest", "--add", "default", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3
    qisrc_action("manifest", "default", "-g", "mygroup")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2

def test_check(qisrc_action, git_server):
    # Get a correct xml file from the server:
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    qisrc_action("manifest", "--add", "default", manifest_url)

    # copy it to an other place, make a mistake, and run --check:
    srv_xml = git_server.src.join("manifest", "manifest.xml")
    manifest = qisrc.manifest.Manifest(srv_xml.strpath)
    editable_path = qisrc_action.tmpdir.join("manifest.xml")
    manifest.manifest_xml = editable_path.strpath
    manifest.add_repo("doestnotexists.git", "nowhere")
    manifest.dump()

    error = qisrc_action("manifest", "--check", "default",
                         editable_path.strpath, raises=True)
    assert "doestnotexists.git" in error
    # running qisrc sync should still work:
    qisrc_action("sync")

    # this time create a correct xml and re-run --check:
    git_server.create_repo("bar.git")
    manifest = qisrc.manifest.Manifest(srv_xml.strpath)
    editable_path = qisrc_action.tmpdir.join("manifest.xml")
    manifest.manifest_xml = editable_path.strpath
    manifest.dump()

    qisrc_action("manifest", "--check", "default", editable_path.strpath)
    git_worktree = TestGitWorkTree()
    assert git_worktree.get_git_project("bar")

    # running qisrc sync just to be sure:
    qisrc_action("sync")
