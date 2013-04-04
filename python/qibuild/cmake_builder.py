import os
import functools

import qibuild.deps_solver

class CMakeBuilder(object):
    def __init__(self, build_worktree, projects):
        self.build_worktree = build_worktree
        self.projects = projects
        self.deps_solver = qibuild.deps_solver.DepsSolver(build_worktree)
        self.dep_types = ["build", "runtime"]

    def configure(self, **kwargs):
        self.write_dependencies_cmake()
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        for project in projects:
            project.configure(**kwargs)

    # pylint: disable-msg=E0213
    def need_configure(func):
        """ Decorator for every function that expects a build directory to
        exist

        """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            projects = self.deps_solver.get_dep_projects(self.projects, ["build"])
            for project in projects:
                if not os.path.exists(project.build_directory):
                    raise NotConfigured(project)
            res = func(self, *args, **kwargs)
            return res
        return new_func

    @need_configure
    def build(self, **kwargs):
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        for project in projects:
            project.build(**kwargs)

    def write_dependencies_cmake(self):
        projects = self.deps_solver.get_dep_projects(self.projects, ["build", "runtime"])
        for project in projects:
            sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build"])
            project.write_dependencies_cmake(sdk_dirs)
            sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build", "runtime"])
            project.write_qi_path_conf(sdk_dirs)

    @need_configure
    def install(self, dest_dir, **kwargs):
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        packages = self.deps_solver.get_dep_packages(self.projects, self.dep_types)
        # runtime boolean is actually a shorthand for dep_types == ["runtime"]
        # FIXME: change the install() method to accept a list of dep types
        # instead
        runtime = self.dep_types == ["runtime"]
        for project in projects:
            project.install(dest_dir, runtime=runtime, **kwargs)
        for package in packages:
            package.install(dest_dir, runtime=runtime, **kwargs)


class NotConfigured(Exception):
    def __init__(self, project):
        self.project = project

    def __str__(self):
        mess = """\
The project {project.name} has not been configured yet.
(The build directory {project.build_directory} does not exist)
Please run `qibuild configure` first
"""
        return mess.format(project=self.project)

