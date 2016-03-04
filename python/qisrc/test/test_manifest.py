## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisrc.manifest
import qisrc.review

import pytest

import mock

def test_simple_read(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar" branch="next"
        remotes="origin" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert len(manifest.repos) == 1
    bar = manifest.repos[0]
    assert bar.src == "lib/bar"
    assert bar.clone_url == "git@example.com:foo/bar.git"
    assert bar.default_branch == "next"

def test_src_are_unique(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar" branch="next"
        remotes="origin" />
  <repo project="bar/bar.git" src="lib/bar" branch="next"
        remotes="origin" />
</manifest>
""")
    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "Found two projects sharing the same sources" in str(e.value)

def test_projects_are_unique(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="bar"  remotes="origin" />
  <repo project="foo/bar.git" src="bar2" remotes="origin" />
</manifest>
""")
    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "foo/bar.git found twice" in str(e.value)

def test_empty_src(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" branch="master" remotes="origin" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    bar = manifest.repos[0]
    assert bar.src == "foo/bar"

def test_no_remotes_attr(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar"/>
</manifest>
""")
    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert e.value.message == "Missing 'remotes' attribute"

def test_several_reviews(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="review1" url="git@example.com" review="true" />
  <remote name="review2" url="git@example.com" review="true" />
</manifest>
""")
    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "Only one" in str(e.value)

def test_no_matching_remote(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar" remotes="invalid" />
</manifest>
""")
    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert e.value.message == "No matching remote: invalid for repo foo/bar.git"

def test_repo_branch(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="bar.git" remotes="origin" />
  <repo project="foo.git" branch="devel" remotes="origin" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    bar = manifest.repos[0]
    foo = manifest.repos[1]
    assert bar.default_branch == "master"
    assert foo.default_branch == "devel"

def test_remote_branch(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" default_branch="release" />
  <repo project="bar.git" remotes="origin" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    bar = manifest.repos[0]
    assert bar.default_branch == "release"

def test_invalid_group(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo.git" remotes="origin" />
  <groups>
    <group name="foo-group">
      <project name="foo.git" />
      <project name="bar.git" />
    </group>
  </groups>

</manifest>
""")
    # pylint: disable-msg=E1101
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        manifest.get_repos(groups=["foo-group"])
    assert "foo-group" in str(e.value)
    assert "bar.git" in str(e.value)
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        manifest.get_repos(groups=["mygroup"])
    assert "No such group: mygroup" in str(e.value)

def test_review_projects(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <remote name="gerrit" url="http://gerrit:8080" review="true" />
  <repo project="foo/bar.git" src="lib/bar" remotes="gerrit" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert len(manifest.repos) == 1
    bar = manifest.repos[0]
    assert bar.src == "lib/bar"
    assert bar.clone_url == "http://gerrit:8080/foo/bar.git"
    assert bar.review is True


def test_review_projects_with_two_remotes(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <remote name="gerrit" url="http://gerrit:8080" review="true" />
  <repo project="foo/bar.git" src="lib/bar" remotes="origin gerrit" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert len(manifest.repos) == 1
    bar = manifest.repos[0]
    assert bar.src == "lib/bar"
    assert len(bar.remotes) == 2
    origin_remote = bar.remotes[0]
    gerrit_remote = bar.remotes[1]
    assert origin_remote.name == "origin"
    assert gerrit_remote.name == "gerrit"
    assert gerrit_remote.review is True
    assert bar.review_remote == gerrit_remote
    assert bar.review == True
    assert bar.default_remote.name == "origin"

def test_no_review(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <remote name="gerrit" url="http://gerrit:8080" review="true" />
  <repo project="foo/bar.git" src="lib/bar" remotes="origin gerrit" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath, review=False)

    assert len(manifest.repos) == 1
    [repo] = manifest.repos
    assert repo.review == False
    assert repo.default_remote.name == "origin"

    assert len(repo.remotes) == 1
    [remote] = repo.remotes
    assert remote.name == "origin"
    assert remote.review is False

def test_default_remote(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <remote name="gerrit" url="http://gerrit:8080" review="true" />
  <repo project="foo.git" src="foo" remotes="origin gerrit"
        default_remote="gerrit" />
  <repo project="bar.git" src="bar" remotes="origin gerrit" />
  <repo project="baz.git" src="baz" remotes="origin" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert manifest.get_repo("foo.git").default_remote.name == "gerrit"
    assert manifest.get_repo("bar.git").default_remote.name == "origin"
    assert manifest.get_repo("baz.git").default_remote.name == "origin"

def test_groups(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="qi/libqi.git" remotes="origin" />
  <repo project="qi/libqimessaging.git" remotes="origin" />
  <repo project="qi/naoqi.git" remotes="origin" />

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
    assert git_projects[0].clone_url == "git@example.com:qi/libqi.git"
    assert git_projects[1].clone_url == "git@example.com:qi/libqimessaging.git"


def test_default_group(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="a.git" remotes="origin" />
  <repo project="b.git" remotes="origin" />
  <repo project="c.git" remotes="origin" />

  <groups>
    <group name="a_group" default="true" >
      <project name="a.git" />
      <project name="b.git" />
    </group>
  </groups>
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    git_projects = manifest.get_repos()
    assert len(git_projects) == 2

def test_default_branch(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <branch default="devel" />
  <repo project="foo/bar.git" src="lib/bar" remotes="origin" />
  <repo project="foo/foo.git" src="lib/foo" remotes="origin" branch="tutu" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert len(manifest.repos) == 2
    assert manifest.default_branch == "devel"
    bar = manifest.repos[0]
    assert bar.default_branch == "devel"
    foo = manifest.repos[1]
    assert foo.default_branch == "tutu"


def test_multiple_remotes(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar" remotes="origin">
    <upstream name="kernel-lts" url="git.kernel.org" />
  </repo>
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert len(manifest.repos) == 1
    foo = manifest.repos[0]
    assert len(foo.remotes) == 2

def test_fixed_ref(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git"
        src="lib/bar"
        remotes="origin"
        ref="v0.1" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    foo = manifest.repos[0]
    assert foo.default_branch is None
    assert foo.fixed_ref == "v0.1"

def test_fixed_ref_and_branch_are_exclusive(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git"
        src="lib/bar"
        remotes="origin"
        ref="v0.1"
        branch="master" />
</manifest>
""")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception)as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "'branch' and 'ref' are mutually exclusive" in e.value.args[0]

def test_from_git_repo(git_server):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.create_repo("bar")
    manifest_repo = git_server.root.join("src", "manifest").strpath
    manifest = qisrc.manifest.from_git_repo(manifest_repo, "master")
    assert len(manifest.repos) == 1
    manifest = qisrc.manifest.from_git_repo(manifest_repo, "devel")
    assert len(manifest.repos) == 2

def test_all_repos(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="a.git" remotes="origin" />
  <repo project="b.git" remotes="origin" />
  <repo project="c.git" remotes="origin" />

  <groups>
    <group name="a_group" default="true" >
      <project name="a.git" />
      <project name="b.git" />
    </group>
  </groups>
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    git_projects = manifest.get_repos(all=True)
    assert len(git_projects) == 3

def test_only_gerrit_no_review(tmpdir, record_messages):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="gerrit" url="git@gerrit.lan" review="true"/>
  <repo project="foo.git" remotes="gerrit" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath, review=False)
    foo_repo = manifest.get_repos()[0]
    assert foo_repo.clone_url is None
    assert record_messages.find("foo.git only has a review remote")

def test_inconsistent_remotes(tmpdir):
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="b.git" remotes="origin">
    <upstream name="origin" url="git@other.org:b.git" />
  </repo>
</manifest>
""")
    # pylint:disable-msg=E1101
    with pytest.raises(Exception) as e:
        manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "has the same name" in e.value.args[0]
