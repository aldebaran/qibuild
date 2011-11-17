## Copyright (C) 2011 Aldebaran Robotics
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
