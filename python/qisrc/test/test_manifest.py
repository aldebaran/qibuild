#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

import qisrc.review
import qisrc.manifest


def test_simple_read(tmpdir):
    """ Test Simple Read """
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
    bar1 = manifest.repos[0]
    assert bar1.src == "lib/bar"
    assert bar1.clone_url == "git@example.com:foo/bar.git"
    assert bar1.default_branch == "next"


def test_src_are_unique(tmpdir):
    """ Test Src Are Unique """
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
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "Found two projects sharing the same sources" in str(e.value)


def test_projects_are_unique(tmpdir):
    """ Test Projects Are Unique """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="bar"  remotes="origin" />
  <repo project="foo/bar.git" src="bar2" remotes="origin" />
</manifest>
""")
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "foo/bar.git found twice" in str(e.value)


def test_empty_src(tmpdir):
    """ Test Empty Src """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" branch="master" remotes="origin" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    bar1 = manifest.repos[0]
    assert bar1.src == "foo/bar"


def test_no_remotes_attr(tmpdir):
    """ Test No Remote Attr """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar"/>
</manifest>
""")
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert e.value.message == "Missing 'remotes' attribute"


def test_several_reviews(tmpdir):
    """ Test Several Reviews """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="review1" url="git@example.com" review="true" />
  <remote name="review2" url="git@example.com" review="true" />
</manifest>
""")
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "Only one" in str(e.value)


def test_no_matching_remote(tmpdir):
    """ Test No Matching Remote """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="foo/bar.git" src="lib/bar" remotes="invalid" />
</manifest>
""")
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert e.value.message == "No matching remote: invalid for repo foo/bar.git"


def test_repo_branch(tmpdir):
    """ Test Repo Branch """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" />
  <repo project="bar.git" remotes="origin" />
  <repo project="foo.git" branch="devel" remotes="origin" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    bar1 = manifest.repos[0]
    foo1 = manifest.repos[1]
    assert bar1.default_branch == "master"
    assert foo1.default_branch == "devel"


def test_remote_branch(tmpdir):
    """ Test Remote Branch """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
<manifest>
  <remote name="origin" url="git@example.com" default_branch="release" />
  <repo project="bar.git" remotes="origin" />
</manifest>
""")
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    bar1 = manifest.repos[0]
    assert bar1.default_branch == "release"


def test_invalid_group(tmpdir):
    """ Test Invalid Group """
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
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        manifest.get_repos(groups=["foo-group"])
    assert "foo-group" in str(e.value)
    assert "bar.git" in str(e.value)
    with pytest.raises(qisrc.manifest.ManifestError) as e:
        manifest.get_repos(groups=["mygroup"])
    assert "No such group: mygroup" in str(e.value)


def test_review_projects(tmpdir):
    """ Test Review Project """
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
    bar1 = manifest.repos[0]
    assert bar1.src == "lib/bar"
    assert bar1.clone_url == "http://gerrit:8080/foo/bar.git"
    assert bar1.review is True


def test_review_projects_with_two_remotes(tmpdir):
    """ Test Review Projects With Two Remotes """
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
    bar1 = manifest.repos[0]
    assert bar1.src == "lib/bar"
    assert len(bar1.remotes) == 2
    origin_remote = bar1.remotes[0]
    gerrit_remote = bar1.remotes[1]
    assert origin_remote.name == "origin"
    assert gerrit_remote.name == "gerrit"
    assert gerrit_remote.review is True
    assert bar1.review_remote == gerrit_remote
    assert bar1.review is True
    assert bar1.default_remote.name == "origin"


def test_no_review(tmpdir):
    """ Test No Review """
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
    assert repo.review is False
    assert repo.default_remote.name == "origin"
    assert len(repo.remotes) == 1
    [remote] = repo.remotes
    assert remote.name == "origin"
    assert remote.review is False


def test_default_remote(tmpdir):
    """ Test Default Remote """
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
    """ Test Groups """
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
    """ Test Default Group """
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
    """ Test Default Branch """
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
    bar1 = manifest.repos[0]
    assert bar1.default_branch == "devel"
    foo1 = manifest.repos[1]
    assert foo1.default_branch == "tutu"


def test_multiple_remotes(tmpdir):
    """ Test Multiple Remotes """
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
    foo1 = manifest.repos[0]
    assert len(foo1.remotes) == 2


def test_fixed_ref(tmpdir):
    """ Test Fixed Ref """
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
    foo1 = manifest.repos[0]
    assert foo1.default_branch is None
    assert foo1.fixed_ref == "v0.1"


def test_fixed_ref_and_branch_are_exclusive(tmpdir):
    """ Test Fixed Ref And Branch are Exclusive """
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
    with pytest.raises(Exception)as e:
        qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "'branch' and 'ref' are mutually exclusive" in e.value.args[0]


def test_from_git_repo(git_server):
    """ Test From Git Repo """
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.create_repo("bar")
    manifest_repo = git_server.root.join("src", "manifest").strpath
    manifest = qisrc.manifest.from_git_repo(manifest_repo, "master")
    assert len(manifest.repos) == 1
    manifest = qisrc.manifest.from_git_repo(manifest_repo, "devel")
    assert len(manifest.repos) == 2


def test_all_repos(tmpdir):
    """ Test All Repo """
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
    git_projects = manifest.get_repos(get_all=True)
    assert len(git_projects) == 3


def test_import_parser(tmpdir):
    """ Test Import Parser """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
    <manifest>
      <remote name="origin" url="git@example.com" />
      <import manifest="a.git" remotes="origin" />
      <import manifest="b.git" remotes="origin" />
    </manifest>
    """)
    manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    import_manifest = manifest.import_manifest
    assert len(import_manifest) == 2
    assert len(import_manifest[0].remote_names) == 1
    assert import_manifest[0].default_remote_name == "origin"
    assert import_manifest[0].remotes[0].url == "git@example.com:a.git"


def test_import_parser_error_manifest(tmpdir):
    """ Test Import Parser Error Manifest """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
    <manifest>
      <remote name="origin" url="git@example.com" />
      <import remotes="origin" />
    </manifest>
    """)
    with pytest.raises(Exception)as e:
        _manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "Missing 'manifest' attribute" in e.value.args[0]


def test_import_parser_error_remote_empty(tmpdir):
    """ Test Import Parser Error Remote Empty """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
    <manifest>
      <remote name="origin" url="git@example.com" />
      <import manifest="a.git" remotes="" />
    </manifest>
    """)
    with pytest.raises(Exception)as e:
        _manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "Empty 'remotes' attribute" in e.value.args[0]


def test_import_parser_error_remote(tmpdir):
    """ Test Import Parser Error Remote """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
    <manifest>
      <remote name="origin" url="git@example.com" />
      <import manifest="a.git"/>
    </manifest>
    """)
    with pytest.raises(Exception)as e:
        _manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "Missing 'remotes' attribute" in e.value.args[0]


def test_import_parser_error_remote_missing(tmpdir):
    """ Test Import Parsder Error Remote Missing """
    manifest_xml = tmpdir.join("manifest.xml")
    manifest_xml.write(""" \
    <manifest>
       <import manifest="a.git" remotes="origin" />
    </manifest>
    """)
    with pytest.raises(Exception)as e:
        _manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
    assert "No matching remote: origin for repo a.git" in e.value.args[0]
