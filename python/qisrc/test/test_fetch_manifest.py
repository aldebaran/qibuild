## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import pytest

import qibuild.sh
import qisrc.sync
from qisrc.test.test_git import create_git_repo
from qisrc.test.test_git import push_file

def create_worktree(tmpdir):
    work = os.path.join(tmpdir, "work")
    qibuild.sh.mkdir(work)
    return qisrc.worktree.create(work)


def test_fetch_manifest(tmpdir):
    tmpdir = tmpdir.strpath
    manifest_url = create_git_repo(tmpdir, "manifest")
    xml = """
<manifest>
<remote fetch="git@foo" name="origin" revision="release-1.12" />
</manifest>
"""
    push_file(tmpdir, "manifest", "manifest.xml", xml)

    worktree = create_worktree(tmpdir)
    qisrc.sync.fetch_manifest(worktree, manifest_url)

    manifest_proj = worktree.get_project("manifest/default")
    manifest_xml = os.path.join(manifest_proj.path, "manifest.xml")
    with open(manifest_xml, "r") as fp:
        assert fp.read() == xml

def test_fetch_manifest_no_default(tmpdir):
    tmpdir = tmpdir.strpath
    manifest_url = create_git_repo(tmpdir, "manifest")

    worktree = create_worktree(tmpdir)

    with pytest.raises(Exception) as e:
        qisrc.sync.fetch_manifest(worktree, manifest_url)

    assert "Could not find a file named manifest.xml" in str(e)
