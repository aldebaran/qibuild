## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

def test_simple_sync(tmpdir, git_server, git_worktree):
    git_server.create_repo("foo.git")
    git_worktree.add_manifest(git_server.manifest)
    git_worktree.sync()
    assert len(git_worktree.projects) == 1
