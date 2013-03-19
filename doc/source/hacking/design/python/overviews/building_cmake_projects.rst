Building CMake projects
=======================

For this overview, we will assume we have:



* A ``foo-sdk`` :term:`toolchain` containing a :term:`packages <package>`,
  named ``bar``

* A :term:`worktree` containing two :term:`projects <project>`,
  the ``world`` project, and a ``hello`` project, which depends on ``world``
  and ``bar``.

* A build profile named ``my-profile`` configured in the worktree.


This overview guides you through all what happens from the moment you run:

.. code-block:: console

 $ qibuild configure --worktree=/path/to/worktree \
                     --config foo-sdk \
                     --profile my-profile \
                     --release \
                     -DWITH_SPAM=ON \
                     hello


to every cmake code that is generated, and what CMake flags are passed.

(We chose a complex example here on purpose to show all the various cases that
need to be handled)

Command line parsing - first pass
---------------------------------

This is done by ``qisys.script.root_command_main`` from
``bin/qibuild`` script.

We look for every module in ``qibuild.actions``, and find the ``configure.py`` module.

Then, we create a ``argparse.ArgumentParser`` parser, and run ``qibuild.configure.configure_parser``
on it.

We parse the command line arguments using this parser, and we now have a ``argparse.NameSpace``
object we can pass to ``qibuild.configure.do``.

.. code-block:: python

   # in qibuild.actions.configure

   def configure_parser(parser):
      # Calls functions in ``qibuild.parsers`` to add all the options
      # this command recognize


   def do(args):
      # In this point we have a argparse.Namespace object with the "raw"
      # result of the arguments parsing
      args.worktree = "/path/to/worktree"
      args.build_type = "Release"
      args.config = "foo-sdk"
      args.projects = ["hello"]
      args.profiles = ["my-profile"]


This "raw" command parsing already took care of simple tasks, like
making sure the ``--debug`` or ``--release`` arguments are converted
to a proper ``CMAKE_BUILD_TYPE``.

Command line parsing - second pass
----------------------------------


Here the ``BuildWorkTree`` and the ``BuildProject`` objects
are initialized using the results of the argument parsing:

.. code-block:: python

    # in qibuild.actions.configure

    def do(args):
      build_worktree = qibuild.parsers.get_build_worktree(args)
      build_projects = qibuild.parsers.get_build_projects(build_worktree, args)


The ``get_`` functions in ``qibuild.parsers`` are here to factorize code
that must be called in every action that uses a BuildWorkTree.

Here's what those functions do:

get_build_worktree
++++++++++++++++++

* A new WorkTree object is initialized using the path given in
  args.worktree, or by exploring parent directories until a ``.qi``
  directory is found if ``--worktree`` is not given
  At this point, every path registered in the worktree can be found
  in ``worktree.projects``

* A new BuildWorkTree is initialized. A list of ``BuildProject`` objects is
  built from every project in ``worktree.projects``, by inspecting the various
  ``qiproject.xml``  and looking for ``<qibuild>`` tags.
  Note that at this moment ``build_project.depends`` and ``build_project.rdepends``
  are **sets** of **names** because no dependency resolution has been done yet.

* A new CMakeBuildConfig object is initialized, using the ``.qi/qibuild.xml`` file to
  read the default config that should be used. If the user has an incorrect
  default config specified in the ``.qi/qibuild.xml`` file, an error is raised
  immediately.

* Then, the ``build_config`` object is configured using the ``args`` object and
  the ``qibuild.xml`` configuration files.

  First, the ``-c`` argument is checked to see if it matches a known toolchain.
  If not, an error is raised.

  Then, the configuration specific settings and the default settings
  in ``~/.config/qi/qibuild.xml`` are read.

  For instance, if the user specified ``-c foo-sdk`` on the command line there is a
  ``<cmake gererator="Ninja">`` tag  in the ``<config name="foo-sdk">``
  section of ``~/.config/qi/qibuild.xml``, ``build_config.cmake_generator`` is set
  to ``Ninja`` and ``build_config.toolchain_name`` to ``foo-sdk``

  Lastly, the options coming from the command line are applied to the
  ``build_config`` object.

  This is done *after* reading the config files, so that settings can be
  overwritten. Thus the user can for instance specify
  ``--cmake-generator="Unix Makefiles"`` to overwrite the default CMake
  generator configured in ``~/.config/qi/qibuild.xml``

* Lastly, the ``build_config`` is applied to the ``BuildWorkTree``:
  ``worktree.build_config = build_config``.


Note: the code later looks like:

.. code-block:: python

  # in BuildProject

  def configure(self, **kwargs)
      cmake_args = self.cmake_args
      build_directory = self.build_directory


But actually, ``cmake_args`` and ``build_directory`` are both properties.

This means that the build dir will always match the latest build settings,
and that the list of CMake args in the BuildProject will always be up to date.

.. code-block:: python

    # in CMakeBuildConfig

    @property
    def cmake_args(self):
        # Transform all the "high level" settings into a list of
        # CMake arguments

    >>> build_config.cmake_generator == "Ninja"
    >>> build_config.cmake_args
    ["-G", "Ninja"]
    >>> build_config.toolchain_name = "foo-sdk"
    >>> build_config.cmake_args
    ["-DCMAKE_TOOLCHAIN_FILE=/path/to/foo-sdk/toolchain.cmake"]

The build config also manages the environment variables, so that
you can for instance set a suitable ``PATH`` when using mingw
on windows without to mess with the registry base.

.. code-block:: python

    # in BuildProject
    @property
    def build_directory(self):
        #  Create a sensible build dir, using
        # self.build_worktree.build_config

    >>> build_config.build_type = "Release"
    >>> hello_project.build_directory = "/path/to/hello/build-release"
    >>> build_config.profiles = ["my-profile"]
    >>> hello_project.build_directory = "/path/to/hello/build-my-profile"



get_build_projects
++++++++++++++++++

The goal here is to get a list of ``BuildProject`` objects to build.

* If no build project named is specified, the parent directories are
  explored until a ``qiproject.xml`` containing a ``<qibuild>`` tag is found.

  If no such project is registered in the ``BuildWorkTree`` yet, it will
  be automatically added to the worktree cache.

* If the user specified some projects in the command line, a matching ``build_project``
  is searched in the ``build_worktree`` for every project name specified on the
  command line. If no build project is found, an error is raised.


Configuring the project and its dependencies
---------------------------------------------


Here's what the code looks like:

.. code-block:: python

  # in qibuild.actions.configure

  cmake_builder = qibuild.build.CMakeBuilder(build_worktree,
                                             build_projects)
  qibuild.parsers.apply_args(cmake_builder, args)
  cmake_builder.configure()



.. code-block:: python

  # in qibuild.parsers

  def apply_args(cmake_builder, args):
      cmake_builder.solving_type = args.solving_type

.. code-block:: python

  # in qibuild.cmake_builder

  class CMakeBuilder:
      def __init__(self, build_worktree, projects):
          self.build_worktree = build_worktree
          self.projects = projects
          self.deps_solver = BuildDepsSolver(self)


      @property
      def build_config(self):
          return self.build_worktree.build_config

      @property
      def cmake_generator(self):
          return self.build_config.cmake_generator

      @property
      def build_env(self):
        return self.build_config.build_env

      @property
      def num_jobs(self):
          # transform the -j argument to a suitable integer,
          # depending on the CMake generator


      def configure(self, **kwargs):
          self._write_dependencies_cmake()
          projects = self.dep_solver.get_projects(self.projects, self.solving_type)
          for project in projects:
              project.configure(env=self.build_env, **kwargs)

      @need_configure
      def build(self, **kwargs):
          projects = self.dep_solver.get_projects(self.projects, self.solving_type)
          for project in projects:
              project.build(env=self.build_env, num_jobs=args.num_jobs, **kwargs)

      @need_configure
      def install(self, dest_dir):
          projects = self.dep_solver.get_projects(self.projects, self.solving_type)
          packages = self.dep_solver.get_packages(self.projects, self.solving_type)
          for project in projects:
              project.install(dest_dir)
          runtime = (self.solving_type == "runtime")
          for package in packages:
              package.install(dest_dir, runtime=runtime)

      def need_configure(self):
          projects = self.dep_solver.get_projects(self.projects, "default")
          for project in projects:
              # check that the build directory exists
              ...

      def _write_dependencies_cmake(self):
         """ Delegates to BuildProject.write_dependencies_cmake """
          projects = self.dep_solver.get_projects(self.projects, "default")
          for project in projects:
              sdk_dirs = self.deps_solver.get_sdk_dirs(project)
              project.write_dependencies_cmake(sdk_dirs)


Note that the ``CMakeBuilder`` contains a ``BuildDepsSolver`` to delegates
all the dependencies solving.

For instance, configuring ``hello``, by default should call ``configure()`` on
the ``world`` project, unless ``-s`` was specified.

Also, since ``hello`` has a runtime dependency on the ``bar`` package,
``qibuild install --runtime hello /tmp/hl`` should install both ``hello``
and ``bar`` to ``/tmp/hl``


Generating the dependencies.cmake
+++++++++++++++++++++++++++++++++

For the ``CMake`` call to work, a ``dependencies.cmake`` must be written
in the build directory

This is done by ``cmake_builder.write_dependencies_cmake``

Here it is important that the ``dependencies.cmake`` always contains the list of every
build dependencies, even if ``-s`` is used.

That's why the solving type is set to ``default`` when calling ``update_projects``


Calling CMake
+++++++++++++

Here ``deps_solver`` honors the ``solving_type``, so that when calling
``qibuild configure -s hello``, ``world.configure()`` is not called.


Installing
++++++++++

When installing a project, the ``deps_solver`` is again used to get a
list of packages to install.

Then either:
 * the whole contents of the packages are installed (the "-config.cmake" files, the
   headers, the static and shared libraries, etc.)
 * if ``solving_type`` was set to ``runtime``, only the runtime parts of the packages
   (shared libraries) will be installed.


Building projects outside a qiBuild action
------------------------------------------

.. code-block:: python

    def build_project(worktree_root, name):
        # Could be part of a continuous integration script, for instance:
        worktree = qisys.worktree.WorkTree(worktree_root)
        build_worktree = BuildWorkTree(worktree)
        build_config = CMakeBuildConfig(build_worktree.qibuild_xml)
        # set build_config.toolchain_name or build_config.build_type here
        # build_config.build_type = "Release"
        build_worktree.build_config = build_worktree
        project = build_worktree.get_build_project(name)
        cmake_builder = CMakeBuilder(build_worktree, [project])
        # set dep_solving type here
        # build_worktree.dep_solving_type = "runtime_only"
        cmake_builder.configure()
        cmake_builder.build()
