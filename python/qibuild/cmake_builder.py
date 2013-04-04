import os
import functools

from qisys import ui
import qibuild.deps_solver

class CMakeBuilder(object):
    def __init__(self, build_worktree, projects):
        self.build_worktree = build_worktree
        self.projects = projects
        self.deps_solver = qibuild.deps_solver.DepsSolver(build_worktree)
        self.dep_types = ["build", "runtime"]

    def configure(self, **kwargs):
        """ Configure the projects in the correct order """
        self.bootstrap_projects()
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)

        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Configuring",
                          ui.blue, project.name)
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
        """ Build the projects in the correct order """
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Building",
                          ui.blue, project.name)
            project.build(**kwargs)

    def bootstrap_projects(self):
        """ Write the dependencies.cmake and the qi/path.conf files for
        every project

        """
        projects = self.deps_solver.get_dep_projects(self.projects, ["build", "runtime"])
        for project in projects:
            sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build"])
            project.write_dependencies_cmake(sdk_dirs)
            sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build", "runtime"])
            project.write_qi_path_conf(sdk_dirs)

    @need_configure
    def install(self, dest_dir, **kwargs):
        """ Install the projects and the packages to the dest_dir """
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        packages = self.deps_solver.get_dep_packages(self.projects, self.dep_types)
        # runtime boolean is actually a shorthand for dep_types == ["runtime"]
        # FIXME: change the install() method to accept a list of dep types
        # instead
        runtime = self.dep_types == ["runtime"]

        # Compute the real path where to install the packages:
        prefix = kwargs.get("prefix", "/")
        prefix = prefix[1:]
        real_dest = os.path.join(dest_dir, prefix)

        ui.info(ui.green, "The following projects")
        for project in projects:
            ui.info(ui.green, " *", ui.blue, project.name)
        if packages:
            ui.info(ui.green, "and the following packages")
            for package in packages:
                ui.info(" *", ui.blue, package.name)
        ui.info(ui.green, "will be installed to", ui.blue, real_dest)

        if runtime:
            ui.info(ui.green, "(runtime components only)")

        if packages:
            print
            ui.info(ui.green, ":: ", "Installing packages")
        for i, package in enumerate(packages):
            ui.info_count(i, len(projects),
                          ui.green, "Insalling",
                          ui.blue, package.name)
            package.install(real_dest, runtime=runtime, **kwargs)

        print
        ui.info(ui.green, ":: ", "Installing projects")
        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Insalling",
                          ui.blue, project.name)
            project.install(dest_dir, runtime=runtime, **kwargs)


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

