## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import pytest

import qisys.sh
import qisrc.sync
from qisrc.test.test_git import create_git_repo
from qisrc.test.test_git import push_file

def create_worktree(tmpdir):
    work = os.path.join(tmpdir, "work")
    qisys.sh.mkdir(work)
    return qisys.worktree.WorkTree(work)


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_fetch_manifest(tmpdir):
    tmpdir = tmpdir.strpath
    manifest_url = create_git_repo(tmpdir, "manifest")
    xml = """
<manifest>
<remote fetch="git@foo" name="origin" revision="release-1.12" />
</manifest>
"""
    push_file(tmpdir, "manifest", "default.xml", xml)

    worktree = create_worktree(tmpdir)
    qisrc.sync.fetch_manifest(worktree, manifest_url)

    manifest_proj = worktree.get_project("manifest/default")
    manifest_xml = os.path.join(manifest_proj.path, "default.xml")
    with open(manifest_xml, "r") as fp:
        assert fp.read() == xml

# pylint: disable-msg=E1101
@pytest.mark.slow
def test_fetch_manifest_no_default(tmpdir):
    tmpdir = tmpdir.strpath
    manifest_url = create_git_repo(tmpdir, "manifest")

    worktree = create_worktree(tmpdir)

    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisrc.sync.fetch_manifest(worktree, manifest_url)

    assert "Could not find a file named 'default.xml'" in str(e)


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_fetch_manifest_custom_profile(tmpdir):
    tmpdir = tmpdir.strpath
    manifest_url = create_git_repo(tmpdir, "manifest")
    xml = """
<manifest>
    <project name="doc/doc.git" src="doc/general" />
    <project name="doc/internal.git" src="doc/internal" />
</manifest>
"""

    push_file(tmpdir, "manifest", "internal.xml", xml)

    worktree = create_worktree(tmpdir)
    qisrc.sync.fetch_manifest(worktree, manifest_url, profile="internal")

    manifest_proj = worktree.get_project("manifest/default")
    manifest_xml = os.path.join(manifest_proj.path, "internal.xml")
    with open(manifest_xml, "r") as fp:
        assert fp.read() == xml
