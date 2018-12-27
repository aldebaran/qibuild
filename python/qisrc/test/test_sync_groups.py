#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Git Transaction """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.sync


def test_sync_groups(git_worktree, git_server):
    """ Test Sync Group """
    git_server.create_group("mygroup", ["foo", "bar"])
    git_server.create_repo("baz")
    manifest_url = git_server.manifest_url
    worktree_syncer = qisrc.sync.WorkTreeSyncer(git_worktree)
    worktree_syncer.configure_manifest(manifest_url)
    groups = qisrc.groups.get_groups(git_worktree)
    assert groups.projects("mygroup") == ["foo", "bar"]
