## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for the Toc object

"""

import os
import platform
import tempfile
import unittest

import qisys
import qibuild
import qitoolchain


class TestToc():
    """ A class that opens a toc object
    in qibuild/test

    To be used in a with statement so that every
    build dir is cleaned afterwards

    """
    def __init__(self, build_type="Debug", cmake_flags=None):
        test_dir = os.path.abspath(os.path.dirname(__file__))
        worktree = qisys.worktree.open_worktree(test_dir)
        self.toc = qibuild.toc.Toc(worktree, build_type=build_type,
                                   cmake_flags=cmake_flags)

    def clean(self):
        """ Clean every build dir """
        for project in self.toc.worktree.projects:
            build_dirs = os.listdir(project.path)
            build_dirs = [x for x in build_dirs if x.startswith("build")]
            build_dirs = [os.path.join(project.path, x) for x in build_dirs]
            for build_dir in build_dirs:
                qisys.sh.rm(build_dir)

    def __enter__(self):
        return self.toc

    def __exit__(self, type, value, tb):
        self.clean()

def pytest_funcarg__toc(request):
    res = TestToc()
    request.addfinalizer(res.clean)
    return res


def pytest_funcarg__toc_release(request):
    res = TestToc(config="release")
    request.addfinalizer(res.clean)
    return res


class TocTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-feed")
        qisys.sh.mkdir(os.path.join(self.tmp, "qi"))
        self.world_package = qitoolchain.Package("world", "package/world")
        self.world_project = qibuild.project.Project(None, "src/world")
        self.world_project.name = "world"
        self.hello_project = qibuild.project.Project(None, "src/hello")
        self.hello_project.name = "hello"
        self.hello_project.depends = ["world"]
        self.toc = qibuild.toc.toc_open(self.tmp)
        self.toc.active_config = "test"
        self.world_project.toc = self.toc
        self.hello_project.toc = self.toc

    def test_src_deps(self):
        self.toc.projects = [self.hello_project, self.world_project]
        self.toc.update_projects()
        hello_sdk_dirs = self.toc.get_sdk_dirs("hello")
        self.assertEquals(hello_sdk_dirs, ["src/world/build-test/sdk"])

    def test_package_wins_on_project(self):
        self.toc.projects = [self.hello_project, self.world_project]
        self.toc.packages = [self.world_package]
        self.toc.update_projects()
        hello_sdk_dirs = self.toc.get_sdk_dirs("hello")
        self.assertEquals(hello_sdk_dirs, list())

    def test_package_wins_on_project_unless_user_asked(self):
        self.toc.projects = [self.hello_project, self.world_project]
        self.toc.packages = [self.world_package]
        self.toc.update_projects()
        self.toc.active_projects = ["world", "hello"]
        hello_sdk_dirs = self.toc.get_sdk_dirs("hello")
        self.assertEquals(hello_sdk_dirs, ["src/world/build-test/sdk"])
        workd_sdk_dirs = self.toc.get_sdk_dirs("world")
        self.assertEquals(workd_sdk_dirs, list())

    def test_custom_sdk_dir(self):
        dot_qi = os.path.join(self.tmp, ".qi")
        qisys.sh.mkdir(dot_qi, recursive=True)
        qibuild_xml = os.path.join(dot_qi, "qibuild.xml")
        with open(qibuild_xml, "w") as fp:
            fp.write("""
<qibuild>
    <build sdk_dir="sdk" />
</qibuild>
"""
)
        # Create a project named hello
        hello_src = os.path.join(self.tmp, "hello")
        qisys.sh.mkdir(hello_src)
        qiproj_xml = os.path.join(hello_src, "qiproject.xml")
        with open(qiproj_xml, "w") as fp:
            fp.write('<project name="hello" />\n')
        hello_cmake = os.path.join(hello_src, "CMakeLists.txt")
        with open(hello_cmake, "w") as fp:
            fp.write("project(hello)\n")

        worktree = qisys.worktree.open_worktree(self.tmp)
        worktree.add_project(hello_src)
        toc = qibuild.toc.toc_open(self.tmp)
        hello_proj = toc.get_project("hello")

        sdk_dirs = dict()
        for config in ["a", "b"]:
            # Create custom a.cmake a b.cmake files so that
            # toc does not complain
            custom_cmake = os.path.join(dot_qi, config + ".cmake")
            with open(custom_cmake, "w") as fp:
                fp.write("# Custom %s cmake config\n" % config)

            class FakeArgs:
                pass
            args = FakeArgs()
            args.config = config
            toc = qibuild.toc.toc_open(self.tmp, args=args)
            sdk_dirs[config] = toc.get_project("hello").sdk_directory

        a_sdk_dir = sdk_dirs["a"]
        b_sdk_dir = sdk_dirs["b"]
        self.assertTrue(a_sdk_dir != b_sdk_dir)

    def tearDown(self):
        qisys.sh.rm(self.tmp)


def test_is_build_folder_name():
    parts = ["sys", platform.system().lower()]
    assert qibuild.toc.is_build_folder_name(parts) is False
    parts.append(platform.machine().lower())
    assert qibuild.toc.is_build_folder_name(parts) is True
    parts.append("release")
    assert qibuild.toc.is_build_folder_name(parts) is True
    parts.append("foo")
    assert qibuild.toc.is_build_folder_name(parts) is False

if __name__ == "__main__":
    unittest.main()
