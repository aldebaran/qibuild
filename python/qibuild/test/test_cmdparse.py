## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import argparse
import os
import contextlib

import pytest

import qibuild.cmdparse
import qisys.interact

class FakePackage():
    def __init__(self, name):
        self.name = name
        self.depends = list()

class FakeToolchain():
    def __init__(self, packages):
        self.packages = list()
        for package in packages:
            self.packages.append(FakePackage(package))
        self.toolchain_file = "toolchain.cmake"

    def get(self, name, raises=False):
        matches = [x for x in self.packages if x.name == name]
        if matches:
            return matches[0]
        if raises:
            raise Exception("No such package: " + name)
        return None

def create_toc(tmpdir, packages=None):
    tmpdir.mkdir(".qi").join("qibuild.xml").write("<qibuild />\n")
    tmpdir.join(".qi").join("worktree.xml").write(""" <worktee>
 <project src="gui/foo" />
 <project src="lib/libfoo" />
 <project src="lib/libbar" />
 <project src="spam/core" />
 <project src="spam/plugins/eggs" />
 <project src="spam/plugins/bacon" />
</worktee>
""")
    foo = tmpdir.mkdir("gui").mkdir("foo")
    foo.join("qiproject.xml").write("""<project name="foo">
 <depends buildtime="true" runtime="true" names="libfoo" />
</project>
""")
    foo.join("CMakeLists.txt").write("")
    libfoo = tmpdir.mkdir("lib").mkdir("libfoo")
    libfoo.join("qiproject.xml").write("""<project name="libfoo">
 <depends buildtime="true" runtime="true" names="libbar" />
 <depends runtime="true" names="png12" />
 <depends buildtime="true" names="gtest" />
</project>
""")
    libfoo.join("CMakeLists.txt").write("")

    libbar = tmpdir.join("lib").mkdir("libbar")
    libbar.join("qiproject.xml").write("""<project name="libbar">
</project>
""")
    libbar.mkdir("src")
    libbar.join("CMakeLists.txt").write("")

    spam = tmpdir.mkdir("spam").mkdir("core")
    spam.join("qiproject.xml").write("""<project name="spam">
 <depends buildtime="true" names="libbar" />
 <depends runtime="true" names="eggs bacon" />
</project>
""")
    spam.join("CMakeLists.txt").write("")
    spam.mkdir("src")

    eggs = tmpdir.join("spam").mkdir("plugins").mkdir("eggs")
    eggs.join("qiproject.xml").write("""<project name="eggs" />""")
    eggs.join("CMakeLists.txt").write("")

    bacon = tmpdir.join("spam").join("plugins").mkdir("bacon")
    bacon.join("qiproject.xml").write("""<project name="bacon" />""")
    bacon.join("CMakeLists.txt").write("")
    tmpdir.mkdir("other")
    toc = qibuild.toc.toc_open(tmpdir.strpath)
    if not packages:
        packages = list()
    toc.toolchain = FakeToolchain(packages)
    toc.packages = toc.toolchain.packages
    return toc


@contextlib.contextmanager
def change_cwd(toc, dir):
    previous_cwd = os.getcwd()
    dest = os.path.join(toc.worktree.root, dir)
    os.chdir(dest)
    yield
    os.chdir(previous_cwd)

def parse_args(toc, *args, **kwargs):
    """ Call qibuild.cmdparse.project_from_args,
    returns a list of qibuild project names

    """
    one_proj = kwargs.get("one_proj")
    parser = argparse.ArgumentParser()
    parser.add_argument("--worktree")
    if one_proj:
        parser.add_argument("project", nargs="?")
    else:
        parser.add_argument("projects", nargs="*")
        parser.add_argument("-a", "--all", action="store_true")
        parser.add_argument("-s", "--single", action="store_true")
        parser.add_argument("--build-deps", action="store_true")
        parser.add_argument("--runtime", action="store_true")
    parsed_args = parser.parse_args(args=args)
    if one_proj:
        return qibuild.cmdparse.project_from_args(toc, parsed_args).name
    else:
        (packages, projects) = qibuild.cmdparse.deps_from_args(toc, parsed_args)
        return ([x.name for x in packages], [x.name for x in projects])

def test_explicit_toc(tmpdir):
    toc = create_toc(tmpdir, packages=["gtest", "png12"])
    # no project name -> raises
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        parse_args(toc, "--worktree", toc.worktree.root)
    assert e.value.message == "Specifying a project name is mandatory when using --worktree"

    # invalid name:
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        parse_args(toc, "--worktree", toc.worktree.root, "doesnotexist")
        assert "No such project" in str(e.value)

    # correct name no dep:
    (packages,  projects) = parse_args(toc, "--worktree", toc.worktree.root, "libbar")
    assert projects == ["libbar"]
    assert packages == list()

    # build dep
    (packages, projects) = parse_args(toc, "--worktree", toc.worktree.root, "libfoo")
    assert projects == ["libbar", "libfoo"]
    assert packages == ["gtest", "png12"]


def test_on_root(tmpdir):
    toc = create_toc(tmpdir)
    with change_cwd(toc, "."):
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            parse_args(toc)
        assert "No project specified" in str(e.value)


def test_guessing(tmpdir):
    toc = create_toc(tmpdir)
    with change_cwd(toc, "lib/libbar/src"):
        (packages, projects) = parse_args(toc)
        assert projects == ["libbar"]
    with change_cwd(toc, "lib/libfoo"):
        (packages, projects) = parse_args(toc)
        assert projects == ["libbar", "libfoo"]

def test_runtime(tmpdir):
    # runtime dep (used by qibuild install --runtime)
    toc = create_toc(tmpdir, packages=["gtest", "png12"])
    (packages, projects) = parse_args(toc, "libfoo", "--runtime")
    assert projects == ["libbar", "libfoo"]
    assert packages == ["png12"]

    # normal dep (used by qibuild install)
    (packages, projects) = parse_args(toc, "libfoo")
    assert projects == ["libbar", "libfoo"]
    assert packages == ["gtest", "png12"]

def test_guessing_not_in_a_project(tmpdir):
    toc = create_toc(tmpdir)
    with change_cwd(toc, "other"):
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            parse_args(toc)
        assert "Could not guess" in e.value.message

def test_package_masks_project(tmpdir):
    toc = create_toc(tmpdir, ["libbar"])
    (_, projects) = parse_args(toc, "libfoo")
    assert projects == ["libfoo"]
    assert  toc.get_sdk_dirs("libfoo") == list()

def test_project_wins_when_explicit(tmpdir):
    toc = create_toc(tmpdir, ["libbar"])
    (_, projects) = parse_args(toc, "libbar", "libfoo")
    assert projects == ["libbar", "libfoo"]
    bar_sdk_dir = toc.get_project("libbar").sdk_directory
    assert  toc.get_sdk_dirs("libfoo") == [bar_sdk_dir]

def test_using_opts(tmpdir):
    toc = create_toc(tmpdir)
    (_, projects) = parse_args(toc, "spam")
    assert projects == ["eggs", "bacon", "libbar", "spam"]
    (_, projects) = parse_args(toc, "--single", "spam")
    assert projects == ["spam"]
    (_, projects) = parse_args(toc, "--build-deps", "spam")
    assert projects == ["libbar", "spam"]

def test_using_paths(tmpdir):
    toc = create_toc(tmpdir)
    (_, projects) = parse_args(toc, "spam/core", "--single")
    assert projects == ["spam"]
    (_, projects) = parse_args(toc, "spam/core/src", "--single")
    assert projects == ["spam"]
    with change_cwd(toc, "other"):
        (_, projects) = parse_args(toc, "../spam/core/src", "--single")
        assert projects == ["spam"]
    with change_cwd(toc, "spam/core/src"):
        (_, projects) = parse_args(toc, "lib/libbar", "--single")
        assert projects == ["libbar"]

def test_project_from_args(tmpdir):
    toc = create_toc(tmpdir)
    with change_cwd(toc, "spam/core/src"):
        proj = parse_args(toc, one_proj=True)
        assert proj == "spam"

def test_add_missing_with_cmake_user_enter_default(tmpdir, interact):
    toc = create_toc(tmpdir)
    tmpdir.join("other").join("qiproject.xml").write('<project name="other" />\n')
    tmpdir.join("other").join("CMakeLists.txt").write("\n")
    interact.answers = dict()
    with change_cwd(toc, "other"):
        proj = parse_args(toc)
        other = toc.get_project("other")
        assert other.name == "other"

def test_add_missing_with_cmake_user_enter_no(tmpdir, interact):
    toc = create_toc(tmpdir)
    tmpdir.join("other").join("qiproject.xml").write('<project name="other" />\n')
    tmpdir.join("other").join("CMakeLists.txt").write("\n")
    # Check that we get a real error
    interact.answers = {"to the worktree" : False}
    with change_cwd(toc, "other"):
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            proj = parse_args(toc)
        assert "No such project" in str(e.value)

def test_add_missing_no_cmake(tmpdir, interact):
    toc = create_toc(tmpdir)
    tmpdir.join("other").join("qiproject.xml").write('<project name="other" />\n')
    interact.answers = dict()
    with change_cwd(toc, "other"):
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            parse_args(toc)
        assert "CMakeLists.txt file at the root" in str(e.value)
        assert "qibuild convert" in str(e.value)

def test_add_missing_bad_parent_proj(tmpdir, interact):
    toc = create_toc(tmpdir)
    tmpdir.join("other").join("qiproject.xml").write('<project name="other" />\n')
    toc.worktree.add_project("other")
    subproj = tmpdir.join("other").mkdir("subproj")
    subproj.join("CMakeLists.txt").write("")
    subproj.join("qiproject.xml").write('<project name="subproj" />\n')
    interact.answers = dict()
    with change_cwd(toc, "other/subproj"):
        proj = parse_args(toc)
        assert toc.get_project("subproj")
