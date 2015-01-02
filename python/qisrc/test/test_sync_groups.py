## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisrc.sync

def test_sync_groups(git_worktree, git_server):
    git_server.create_group("mygroup", ["foo", "bar"])
    git_server.create_repo("baz")
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest(manifest_url)

    groups = qisrc.groups.get_groups(git_worktree)
    assert groups.projects("mygroup") == ["foo", "bar"]
