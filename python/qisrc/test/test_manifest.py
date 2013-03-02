## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisrc.manifest

import pytest

def test_simple_read(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar" default_branch="next" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)

    assert len(manifest.repos) == 1
    bar = manifest.repos[0]
    assert bar.src == "lib/bar"
    assert bar.remote_url == "git@example.com:foo/bar.git"
    assert bar.default_branch == "next"

def test_no_matching_remote(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar" remote="invalid" />
</manifest>
""")
    # pylint: disable-msg: E1101
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert e.value.message == "No matching remote: invalid for repo foo/bar.git"

def test_review_projects(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <remote name="gerrit" url="http://gerrit:8080" review="true" />
  <repo project="foo/bar.git" src="lib/bar" remote="gerrit" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert len(manifest.repos) == 1
    bar = manifest.repos[0]
    assert bar.src == "lib/bar"
    assert bar.remote_url == "http://gerrit:8080/foo/bar.git"
    assert bar.review == True

def test_groups(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="qi/libqi.git" />
  <repo project="qi/libqimessaging.git" />
  <repo project="qi/naoqi.git" />

  <groups>
    <group name="qim">
      <project name="qi/libqi.git" />
      <project name="qi/libqimessaging.git" />
    </group>
  </groups>
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    git_projects = manifest.get_repos(groups=["qim"])
    assert len(git_projects) == 2
    assert git_projects[0].remote_url == "git@example.com:qi/libqi.git"
    assert git_projects[1].remote_url == "git@example.com:qi/libqimessaging.git"
