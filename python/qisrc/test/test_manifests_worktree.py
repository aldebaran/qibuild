import qisrc.manifests_worktree

import mock

def test_stores_url_and_groups(git_worktree, git_server):
    manifest_url = git_server.manifest_url
    manifests_worktree = qisrc.manifests_worktree.ManifestsWorkTree(git_worktree)
    manifests_worktree.add_manifest("default", manifest_url, groups=["qim"])

    manifests_worktree = qisrc.manifests_worktree.ManifestsWorkTree(git_worktree)
    manifests = manifests_worktree.manifests
    assert len(manifests) == 1
    default_manifest = manifests["default"]
    assert default_manifest.name == "default"
    assert default_manifest.url == manifest_url
    assert default_manifest.groups == ["qim"]

def test_updates_manifests_when_loading(git_worktree, git_server):
    manifest_url = git_server.manifest_url
    manifests_worktree = qisrc.manifests_worktree.ManifestsWorkTree(git_worktree)
    manifests_worktree.add_manifest("default", manifest_url)
    default_xml = git_worktree.tmpdir.join(".qi", "manifests",
                                           "default", "manifest.xml")

    # Push a random file
    git_server.push_file("manifest.git", "a_file", "some contents\n")
    manifests_worktree.load_manifests()
    a_file = git_worktree.tmpdir.join(".qi", "manifests",
                                      "default", "a_file")
    assert a_file.read() == "some contents\n"

