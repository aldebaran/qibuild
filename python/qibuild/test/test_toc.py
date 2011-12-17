## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Automatic testing for the Toc object

"""

import os
import tempfile
import unittest

import qibuild
import qitoolchain

class TocTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-feed")
        qibuild.sh.mkdir(os.path.join(self.tmp, "qi"))
        self.world_package = qitoolchain.Package("world", "package/world")
        self.world_project = qibuild.project.Project("world", "src/world")
        self.hello_project = qibuild.project.Project("hello", "src/hello")
        self.world_project.build_directory = "src/world/build"
        self.hello_project.build_directory = "src/hello/build"
        self.hello_project.depends = ["world"]
        self.toc = qibuild.toc.Toc(self.tmp)

    def test_src_deps(self):
        self.toc.projects = [self.hello_project, self.world_project]
        hello_sdk_dirs = self.toc.get_sdk_dirs("hello")
        self.assertEquals(hello_sdk_dirs, ["src/world/build/sdk"])

    def test_package_wins_on_project(self):
        self.toc.projects = [self.hello_project, self.world_project]
        self.toc.packages = [self.world_package]
        hello_sdk_dirs = self.toc.get_sdk_dirs("hello")
        self.assertEquals(hello_sdk_dirs, list())

    def test_package_wins_on_project_unless_user_asked(self):
        self.toc.projects = [self.hello_project, self.world_project]
        self.toc.packages = [self.world_package]
        self.toc.active_projects = ["world", "hello"]
        hello_sdk_dirs = self.toc.get_sdk_dirs("hello")
        self.assertEquals(hello_sdk_dirs, ["src/world/build/sdk"])
        workd_sdk_dirs = self.toc.get_sdk_dirs("world")
        self.assertEquals(workd_sdk_dirs, list())


    def tearDown(self):
        qibuild.sh.rm(self.tmp)



if __name__ == "__main__":
    unittest.main()

