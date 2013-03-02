## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

def test_new_repos(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.add_manifest("default", manifest_url)
    assert git_worktree.get_git_project("foo")

def test_moving_repos(git_worktree, git_server):
    git_server.create_repo("foo.git")
    manifest_url = git_server.manifest_url
    git_worktree.add_manifest("default", manifest_url)
    git_server.move_repo("foo.git", "foo", "lib/foo")
    git.worktree.load_manifests()
