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
"""Testing DependenciesSolver class

"""

import unittest


from qibuild.dependencies_solver import DependenciesSolver


class Project:
    def __init__(self, name):
        self.name = name
        self.depends = list()
        self.rdepends = list()

class Package:
    def __init__(self, name):
        self.name = name
        self.depends = list()

class DependenciesSolverTestCase(unittest.TestCase):

    def test_bad_solve(self):
        world = Project("world")
        projects = [world]
        packages = []
        dep_solver = DependenciesSolver(projects=projects, packages=packages)
        self.assertRaises(Exception, dep_solver.solve, "foo")

    def test_unknown_dep(self):
        world = Project("world")
        hello = Project("hello")
        hello.depends = ["world"]
        world.depends = ["not_found"]
        projects = [world, hello]
        packages = []
        dep_solver = DependenciesSolver(projects=projects, packages=packages)
        (projects, packages, not_found) = dep_solver.solve(["hello"])
        self.assertEquals(projects,  ["world", "hello"])
        self.assertEquals(packages,  [])
        self.assertEquals(not_found, ["not_found"])

    def test_package_dep(self):
        world = Package("world")
        hello = Project("hello")
        hello.depends = ["world"]
        projects = [hello]
        packages = [world]

        dep_solver = DependenciesSolver(projects=projects, packages=packages)
        (projects, packages, not_found) = dep_solver.solve(["hello"])
        self.assertEquals(projects,  ["hello"])
        self.assertEquals(packages,  ["world"])
        self.assertEquals(not_found, [])

    def test_project_dep(self):
        world = Project("world")
        hello = Project("hello")
        hello.depends = ["world"]
        projects = [hello, world]
        packages = []

        dep_solver = DependenciesSolver(projects=projects, packages=packages)
        (projects, packages, not_found) = dep_solver.solve(["hello"])
        self.assertEquals(projects,  ["world", "hello"])
        self.assertEquals(packages,  [])
        self.assertEquals(not_found, [])

    def test_package_dep_wins_on_project_dep(self):
        world_package = Package("world")
        world_project = Project("world")
        hello = Project("hello")
        hello.depends = ["world"]
        projects = [hello, world_project]
        packages = [world_package]
        dep_solver = DependenciesSolver(projects=projects, packages=packages)
        (projects, packages, not_found) = dep_solver.solve(["hello"])
        self.assertEquals(projects,  ["hello"])
        self.assertEquals(packages,  ["world"])
        self.assertEquals(not_found, [])

    def test_package_dep_wins_on_project_dep_unless_user_asked(self):
        world_package = Package("world")
        world_project = Project("world")
        hello = Project("hello")
        hello.depends = ["world"]
        projects = [hello, world_project]
        packages = [world_package]
        dep_solver = DependenciesSolver(projects=projects, packages=packages)
        (projects, packages, not_found) = dep_solver.solve(["hello", "world"])
        self.assertEquals(projects,  ["world", "hello"])
        self.assertEquals(packages,  [])
        self.assertEquals(not_found, [])

    def test_runtime_args(self):
        static_lib = Project("static-lib")
        big_lib    = Project("big-lib")
        my_exe     = Project("my-exe")

        my_exe.depends = ["big-lib"]
        my_exe.rdepends = ["big-lib"]

        big_lib.depends = ["static-lib"]
        big_lib.rdepends = []

        projects = [static_lib, big_lib, my_exe]
        packages = []
        dep_solver = DependenciesSolver(projects=projects, packages=packages)
        (projects, packages, not_found) = dep_solver.solve(["my-exe"], runtime=True)
        self.assertEquals(projects,  ["big-lib", "my-exe"])
        self.assertEquals(packages,  [])
        self.assertEquals(not_found, [])

if __name__ == "__main__":
    unittest.main()
