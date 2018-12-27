#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Sync Import """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys
from qisrc.test.conftest import TestGitWorkTree


def test_import_manifest(cd_to_tmpdir, tmpdir, git_server):
    """ Test Import Manifest """
    git_server.create_repo("foo_manifest.git")
    git_server.create_repo("bar.git")
    git_server.create_repo("foo.git")
    git_server.create_repo("baz.git")
    content = (""" \
    <manifest>
      <remote name="origin" url="%s/git/srv" />
      <repo branch="master" project="baz.git" remotes="origin" />
      <import manifest="foo_manifest.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("manifest.git", "manifest.xml", content % tmpdir)
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="%s/git/srv" />
        <repo branch="master" project="foo.git" remotes="origin" src="foo" />
        <repo branch="master" project="bar.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("foo_manifest.git", "manifest.xml", content % tmpdir)
    qisys.script.run_action("qisrc.actions.init",
                            [git_server.manifest_url])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3


def test_import_manifest_default_branch(cd_to_tmpdir, tmpdir, git_server):
    """ Test Import Manifest Default Branch """
    git_server.create_repo("foo_manifest.git")
    git_server.create_repo("bar.git")
    git_server.create_repo("foo.git")
    git_server.push_file("manifest.git", "manifest.xml", "<manifest />")
    content = (""" \
    <manifest>
      <remote name="origin" url="file://%s/git/srv" />
      <import manifest="foo_manifest.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("manifest.git", "manifest.xml", content % tmpdir, branch="devel")
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="file://%s/git/srv" />
        <repo branch="master" project="foo.git" remotes="origin" src="foo" />
        <repo branch="master" project="bar.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("foo_manifest.git", "manifest.xml", content % tmpdir, branch="devel")
    qisys.script.run_action("qisrc.actions.init",
                            [git_server.manifest_url, "--branch", "devel"])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2


def test_import_manifest_recursive(cd_to_tmpdir, tmpdir, git_server):
    """ Test Import Manifest Recursive """
    git_server.create_repo("foo_manifest.git")
    git_server.create_repo("bar_manifest.git")
    git_server.create_repo("bar.git")
    git_server.create_repo("foo.git")
    git_server.create_repo("baz.git")
    content = (""" \
    <manifest>
      <remote name="origin" url="file://%s/git/srv" />
      <repo branch="master" project="baz.git" remotes="origin" />
      <import manifest="foo_manifest.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("manifest.git", "manifest.xml", content % tmpdir)
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="file://%s/git/srv" />
        <repo branch="master" project="foo.git" remotes="origin" src="foo" />
        <import manifest="bar_manifest.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("foo_manifest.git", "manifest.xml", content % tmpdir)
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="file://%s/git/srv" />
        <repo branch="master" project="bar.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("bar_manifest.git", "manifest.xml", content % tmpdir)
    qisys.script.run_action("qisrc.actions.init",
                            [git_server.manifest_url])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3


def test_import_manifest_branch(cd_to_tmpdir, tmpdir, git_server):
    """ Test Import Manifest Branch """
    git_server.create_repo("foo_manifest.git")
    git_server.create_repo("bar_manifest.git")
    git_server.create_repo("bar.git")
    git_server.create_repo("foo.git")
    git_server.create_repo("baz.git")
    content = (""" \
    <manifest>
      <remote name="origin" url="file://%s/git/srv" />
      <repo branch="master" project="baz.git" remotes="origin" />
      <import manifest="foo_manifest.git" remotes="origin" branch="devel"/>
    </manifest>
    """)
    git_server.push_file("manifest.git", "manifest.xml", content % tmpdir)
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="file://%s/git/srv" />
        <repo branch="master" project="foo.git" remotes="origin" src="foo" />
    </manifest>
    """)
    git_server.push_file("foo_manifest.git", "manifest.xml", content % tmpdir)
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="file://%s/git/srv" />
        <repo branch="master" project="foo.git" remotes="origin" src="foo" />
        <import manifest="bar_manifest.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("foo_manifest.git", "manifest.xml", content % tmpdir, branch="devel")
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="file://%s/git/srv" />
        <repo branch="master" project="bar.git" remotes="origin" />
    </manifest>
    """)
    git_server.push_file("bar_manifest.git", "manifest.xml", content % tmpdir)
    qisys.script.run_action("qisrc.actions.init",
                            [git_server.manifest_url])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3


def test_import_manifest_group(cd_to_tmpdir, tmpdir, git_server):
    """ Test Import Manifest Group """
    git_server.create_repo("foo_manifest.git")
    git_server.create_repo("bar.git")
    git_server.create_repo("foo.git")
    git_server.create_repo("baz.git")
    content = (""" \
    <manifest>
      <remote name="origin" url="%s/git/srv" />
      <repo branch="master" project="baz.git" remotes="origin" />
      <import manifest="foo_manifest.git" remotes="origin" />

       <groups>
            <group name="baz">
                <project name="baz.git"/>
            </group>
       </groups>

    </manifest>
    """)
    git_server.push_file("manifest.git", "manifest.xml", content % tmpdir)
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="%s/git/srv" />
        <repo branch="master" project="foo.git" remotes="origin" src="foo" />
        <repo branch="master" project="bar.git" remotes="origin" />

        <groups>
            <group name="foo">
                <project name="foo.git"/>
                <project name="bar.git"/>
            </group>
        </groups>

    </manifest>
    """)
    git_server.push_file("foo_manifest.git", "manifest.xml", content % tmpdir)
    qisys.script.run_action("qisrc.actions.init",
                            [git_server.manifest_url, "--group", "foo"])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2


def test_import_manifest_add_group(cd_to_tmpdir, tmpdir, git_server, qisrc_action):
    """ Test Import Manifest Add Group """
    git_server.create_repo("foo_manifest.git")
    git_server.create_repo("bar.git")
    git_server.create_repo("foo.git")
    git_server.create_repo("baz.git")
    content = (""" \
    <manifest>
      <remote name="origin" url="%s/git/srv" />
      <repo branch="master" project="baz.git" remotes="origin" />
      <import manifest="foo_manifest.git" remotes="origin" />

      <groups>
            <group name="baz">
                <project name="baz.git"/>
            </group>
       </groups>

    </manifest>
    """)
    git_server.push_file("manifest.git", "manifest.xml", content % tmpdir)
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="%s/git/srv" />
        <repo branch="master" project="foo.git" remotes="origin" src="foo" />
        <repo branch="master" project="bar.git" remotes="origin" />

        <groups>
            <group name="foo">
                <project name="foo.git"/>
                <project name="bar.git"/>
            </group>
        </groups>

    </manifest>
    """)
    git_server.push_file("foo_manifest.git", "manifest.xml", content % tmpdir)
    qisrc_action("init", git_server.manifest_url, "--group", "baz")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1
    qisrc_action("add-group", "foo")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3


def test_import_manifest_group_use_imported_group(cd_to_tmpdir, tmpdir, git_server, qisrc_action):
    """ Test Import Manifest Group Use Imported Group """
    git_server.create_repo("foo_manifest.git")
    git_server.create_repo("bar.git")
    git_server.create_repo("foo.git")
    git_server.create_repo("baz.git")
    content = (""" \
    <manifest>
      <remote name="origin" url="%s/git/srv" />
      <repo branch="master" project="baz.git" remotes="origin" />
      <import manifest="foo_manifest.git" remotes="origin" />

      <groups>
            <group name="baz">
                <group name="foo"/>
                <project name="baz.git"/>
            </group>
       </groups>

    </manifest>
    """)
    git_server.push_file("manifest.git", "manifest.xml", content % tmpdir)
    content = (""" \
    <manifest>
        <remote name="origin" review="false" url="%s/git/srv" />
        <repo branch="master" project="foo.git" remotes="origin" src="foo" />
        <repo branch="master" project="bar.git" remotes="origin" />

        <groups>
            <group name="foo">
                <project name="foo.git"/>
                <project name="bar.git"/>
            </group>
        </groups>

    </manifest>
    """)
    git_server.push_file("foo_manifest.git", "manifest.xml", content % tmpdir)
    qisrc_action("init", git_server.manifest_url, "--group", "baz")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3
