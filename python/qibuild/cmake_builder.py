import os
import functools

from qisys import ui
import qisys.sh
import qibuild.deps_solver

class CMakeBuilder(object):
    def __init__(self, build_worktree, projects):
        self.build_worktree = build_worktree
        self.projects = projects
        self.deps_solver = qibuild.deps_solver.DepsSolver(build_worktree)
        self.dep_types = ["build", "runtime"]


    # pylint: disable-msg=E0202
    @property
    def dep_types(self):
        """ The list of dependencies to use """
        return qibuild.deps_solver.dep_types

    # pylint: disable-msg=E1101
    @dep_types.setter
    # pylint: disable-msg=E0102
    def dep_types(self, value):
        qibuild.deps_solver.dep_types = value

    @property
    def build_config(self):
        """ The :py:class:`.CMakeBuildConfig` to use when building projects

        """
        return self.build_worktree.build_config

    @property
    def build_env(self):
        """ The environment used when building projects

        """
        return self.build_config.build_env

    @property
    def toolchain(self):
        """ The :py:class:`.Toolchain` to use when building """
        return self.build_config.toolchain

    # pylint: disable-msg=E0213
    def need_configure(func):
        """ Decorator for every function that expects a build directory to
        exist

        """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
            for project in projects:
                if not os.path.exists(project.cmake_cache):
                    raise NotConfigured(project)
            # pylint: disable-msg=E1102
            res = func(self, *args, **kwargs)
            return res
        return new_func

    def bootstrap_projects(self):
        """ Write the dependencies.cmake and the qi/path.conf files for
        every project

        """
        projects = self.deps_solver.get_dep_projects(self.projects, ["build", "runtime"])
        # subtle diffs here: dependencies.cmake must be written for *all* projects,
        # with the build dependencies
        for project in projects:
            sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build"])
            project.write_dependencies_cmake(sdk_dirs)

        # path.conf must be written right before cmake is called, and with
        # all the dependencies
        projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        for project in projects:
            sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build", "runtime", "test"])
            project.write_qi_path_conf(sdk_dirs)

    def pre_build(self, project):
        """ Called before building a project """
        sdk_dirs = self.deps_solver.get_sdk_dirs(project, ["build", "runtime"])
        paths = sdk_dirs[:]
        packages = self.deps_solver.get_dep_packages([project], ["build", "runtime"])
        paths.extend([package.path for package in packages])
        project.fix_shared_libs(paths)

    def configure(self, **kwargs):
        """ Configure the projects in the correct order """
        self.bootstrap_projects()
        if self.dep_types == list():
            projects = self.projects
        else:
            projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)

        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Configuring",
                          ui.blue, project.name)
            project.configure(**kwargs)

    @need_configure
    def build(self, **kwargs):
        """ Build the projects in the correct order """
        if self.dep_types == list():
            projects = self.projects
        else:
            projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Building",
                          ui.blue, project.name)
            self.pre_build(project)
            project.build(**kwargs)

    @need_configure
    def install(self, dest_dir, **kwargs):
        """ Install the projects and the packages to the dest_dir """
        if self.dep_types == list():
            projects = self.projects
        else:
            projects = self.deps_solver.get_dep_projects(self.projects, self.dep_types)
        packages = self.deps_solver.get_dep_packages(self.projects, self.dep_types)

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

        runtime_only = self.dep_types == ["runtime"]
        if runtime_only:
            ui.info(ui.green, "(runtime components only)")

        if packages:
            print
            ui.info(ui.green, ":: ", "Installing packages")
        for i, package in enumerate(packages):
            ui.info_count(i, len(packages),
                          ui.green, "Installing",
                          ui.blue, package.name)
            package.install(real_dest, runtime=runtime_only)

        print
        ui.info(ui.green, ":: ", "Installing projects")
        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Installing",
                          ui.blue, project.name)
            project.install(dest_dir, **kwargs)

    @need_configure
    def deploy(self, url, use_rsync=True, port=22, split_debug=False, with_tests=False):
        """ Deploy the project and the packages it depends to a remote url """
        if self.dep_types == list(): # used -s
            dep_packages = list()
            dep_projects = self.projects
        else:
            dep_packages = self.deps_solver.get_dep_packages(self.projects,
                                                             self.dep_types)
            dep_projects = self.deps_solver.get_dep_projects(self.projects,
                                                             self.dep_types)
        ui.info(ui.green, "The following projects")
        for project in dep_projects:
            ui.info(ui.green, " *", ui.blue, project.name)
        if dep_packages:
            ui.info(ui.green, "and the following packages")
            for package in dep_packages:
                ui.info(" *", ui.blue, package.name)
        ui.info(ui.green, "will be deployed to", ui.blue, url)

        # Deploy packages: install all of them in the same temp dir, then
        # deploy this temp dir to the target
        if dep_packages:
            print
            ui.info(ui.green, ":: ", "Deploying packages")
            with qisys.sh.TempDir() as tmp:
                for i, package in enumerate(dep_packages):
                    ui.info_count(i, len(dep_packages),
                        ui.green, "Deploying package", ui.blue, package.name,
                        ui.green, "to", ui.blue, url)
                    package.install(tmp, runtime=True)
                qibuild.deploy.deploy(tmp, url, use_rsync=use_rsync, port=port)


        print
        ui.info(ui.green, ":: ", "Deploying projects")
        # Deploy projects: install them inside a 'deploy' dir inside the build dir,
        # then deploy this dir to the target
        for (i, project) in enumerate(dep_projects):
            ui.info_count(i, len(dep_projects),
                    ui.green, "Deploying project", ui.blue, project.name,
                    ui.green, "to", ui.blue, url)
            project.deploy(url, split_debug=split_debug, with_tests=with_tests)

        print
        for project in self.projects:
            qibuild.deploy.generate_debug_scripts(self, project.name, url)

class NotConfigured(Exception):
    def __init__(self, project):
        self.project = project

    def __str__(self):
        mess = """\
The project {project.name} has not been configured yet.
Please run `qibuild configure` first
"""
        return mess.format(project=self.project)
