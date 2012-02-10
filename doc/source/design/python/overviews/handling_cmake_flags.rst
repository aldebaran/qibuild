.. _handling-cmake-flags:

Handling CMake flags
====================

For this overview, we will assume we have:

* A ``foo-sdk`` :term:`toolchain` containing a :term:`packages <package>`,
  named ``world``

* A :term:`worktree` containing two :term:`projects <project>`,
  the ``world`` project (sources of the ``world`` packages), and
  an ``hello`` project, which depends on ``world``


This overview guides you through all what
happends from the moment you run

.. code-block:: console

 $ qibuild configure --worktree /path/to/worktree -c foo-sdk --release -DWITH_EGGS=ON hello


To every cmake code that is generated, and what
CMake flags are passed.


Command line parsing
---------------------

This is done by :py:func:`qibuild.cmdline.root_command_main` from
``bin/qibuild`` script.

We look for every module in ``qibuild.actions``, and find the ``configure.py`` module.

Then, we create a ``argparse.ArgumentParser`` parser, and run ``qibuild.configure.configure_parser``
on it.

We parse the command line arguments using this parser, and we now have a ``argparse.NameSpace``
object we can pass to ``qibuild.configure.do``.

.. code-block:: python

   # in qibuild.actions.configure

   def configure_parser(parser):
      # Parse the -c and --worktree option
      qibuild.parsers.toc_parser(parser)
      # Parse the --release and -D options
      qibuild.parsers.build_parser(parser)
      # Parse the [hello] list of projects
      qibuild.parsers.project_parser(parser)


   def do(args):

      # In this point we have:
      arsg.work_tree = "/path/to/worktree"
      args.config = "foo-sdk"
      args.build_type = "release"
      args.project_names = ["hello"]


Building the toc object
------------------------

.. code-block:: python

    # in qibuild.actions.configure

    def do(args):

        toc = qibuild.toc_open(args.worktree, args)


The :py:class:`Toc <qibuild.toc.Toc>` object is built by the :py:func:`qibuild.toc_open`
function.

.. code-block:: python

    # in qibuild.toc.toc_open

    def toc_open(worktree, args):

        # Lots of code like:
        cmake_flags = list()
        if hasattr(args, 'cmake_flags'):
          cmake_flags = args.cmake_flags


    toc = Toc(work_tree,
               config=config,
               build_type=build_type,
               cmake_flags=cmake_flags,
               cmake_generator=cmake_generator,
               path_hints=path_hints,
               qibuild_cfg=qibuild_cfg)

    (active_projects, single) =  _projects_from_args(toc, args)
    toc.active_projects = active_projects

Note how the ``argparse.NameSpace`` object is exploded to become explicit keywork arguments
to the Toc constructor.

This decouples the ``Toc`` initialization from the command line parsing, which is a good
thing.

You may wonder why we we set the ``toc.active_projects`` here and not it Toc ctor.
Well, that's an other story, so more on this later.

Back to the :py:meth:`toc() <qibuild.toc.Toc.__init__>` call.

Toc constructor does a *lot* of stuff (this comes from the fact that the Toc class is huge).

But basically we need to

* Have sane defaults  (for instance 'Unix Makefiles' for the ``cmake_generator``.

* Possibly overwrite these defaults from various config files (the global ``qibuild.xml``
  config file, the local ``.qi/qibuild.xml``, the custom cmake file in
  ``.qi/foo-sdk.cmake``)

* Possibly overwrite these with command line options

Excerpt:

.. code-block:: python

    class Toc:

        def __init__(self, config=None, cmake_flags=None, cmake_generator=None):

            # Set the active configuration.
            # Reading the default config name, merging the default and global
            # config file, and getting the default config to use from the config
            # files is done by the qibuild.config.QiBuildConfig class
            self.config = qibuid.config.QiBuildConfig(config)
            self.active_config = self.config.active_config

            # Set cmake generator if user has not set if in Toc ctor:
            self.cmake_generator = cmake_generator
            if not self.cmake_generator:
                self.cmake_generator = self.config.cmake.generator
                if not self.cmake_generator:
                    self.cmake_generator = "Unix Makefiles"


For the cmake flags it is a bit more complicated.


The flags are given are kept in ``self.user_cmake_flags``.

.. code-block:: python

    class Toc:
        def __init__(self, cmake_flags=None, cmake_generator=None):
            if cmake_flags:
                self.user_cmake_flags = cmake_flags[:]
            else:
                self.user_cmake_flags = list()


And then the computation of the exact cmake flags to use is done
inside the `qibuild.project.Project` class


Computation of projects cmake flags
-----------------------------------

This is done by the :py:func:`qibuild.project.update_project` function during
the Toc construction


.. code-block:: python

    # in qibuild.toc

    class Toc:

        def __init__(self, cmake_flags=None, cmake_generator=None):

            self.update_projects()


        def update_projects(self):

            for project in self.projects:
                qibuild.project.update_project(project, self)


    # in qibuild.project


    def update_project(project, toc):

        # Handle custom global build directory containing all projects
        singlebdir = toc.config.local.build.build_dir

        project.build_directory = ...


        if toc.build_type:
            project.cmake_flags.append("CMAKE_BUILD_TYPE=%s" % (toc.build_type.upper()))

        # add cmake flags
        if toc.user_cmake_flags:
            project.cmake_flags.extend(toc.user_cmake_flags)

        # add the toolchain file:
        if toc.toolchain is not None:
            tc_file = toc.toolchain.toolchain_file
            toolchain_path = qibuild.sh.to_posix_path(tc_file)
            project.cmake_flags.append('CMAKE_TOOLCHAIN_FILE=%s' % toolchain_path)





Generation of CMake code
-------------------------


Toolchain.cmake file generation
+++++++++++++++++++++++++++++++

This occurs because the ``-c`` option given as parameter
on the command line matches a known toolchain.


The first one is generated during the toc initialization

.. code-block:: python

    class Toc:

        def __init__(self, config=None):


            if self.active_config is not None:

                toolchain = qitoolchain.Toolchain(active_config)



During the qitoolchain.Toolchain constructor, we go through the list of packages
to make sure we set CMAKE_FIND_ROOT_PATH correctly

If our case, there is a ``world`` package in the ``foo-sdk`` toolchain, so
the file will look like

.. code-block:: cmake

   list(INSERT CMAKE_FIND_ROOT_PATH 0 "/path/to/world/package")


Generating the dependencies.cmake file
+++++++++++++++++++++++++++++++++++++++


Here we need ``hello`` to be able to find the ``world``

First case:

.. code-block:: console

   $ qibuild configure hello

``hello`` must use the ``world-config.cmake`` from the ``world`` package

Second case:

.. code-block:: console

   $ qibuild configure world hello

``hello`` must use the ``world-config.cmake`` from ``src/world/build/sdk/``.

In the first case, the toolchain file is enough, so everything works fine.

The ``dependencies.cmake`` in the second case.

So, let's what happens there in the two cases.

.. code-block:: python


    # qibuild.toc


    def toc_open(work_tree, args):

        # args.projects contains ["world", "hello"], in the second case,
        # and just ["hello"] in the first case.
        # after command line parsing
        (active_projects, single) =  _projects_from_args(toc, args)
        toc.active_projects = active_projects


    def _projects_from_args(toc, args):
        """
        Cases handled:
          - nothing specified: get the project from the cwd
          - args.single: do not resolve dependencies
          - args.all: return all projects
        Returns a tuple (project_names, single):
            project_names: the actual list for project
            single: user specified --single
        """
        ....


So, we have updated every project, the cmake flags are correct, but we
still have to tell cmake it should insert ``/path/to/worktree/world/build/sdk``
at the beginning of ``CMAKE_FIND_ROOT_PATH``

So, how does this work?


.. code-block:: python

    # qibuild.actions.configure

    toc = toc_open(args.work_tree, args)

    # Note how toc.active_projects has been set
    # (to ['world', 'hello'], but no depency resolution
    # has still occured, because we need to know about the packages
    # in the toolchain, the names of the projects in the work tree,
    # and so on.
    (project_names, _, _) = toc.resolve_deps()


    # qibuild.toc

    class Toc:
        def resolve_deps(self):
            # use a DependenciesSolver with self.projects, self.packages
            # and self.active_projects
            dep_solver = ...
            return dep_solver.solve(...)


So project_names is ["hello"] in the first case, because the ``DependenciesSolver``
saw the 'world' dependency was provided by a package, and ["world", "hello"]
because of the ``active_projects`` argument passed to the ``DependenciesSolver``

.. seealso::

    * :py:class:`DependenciesSolver`

.. code-block:: python

    # qibuild.actions.configure

    projects = [toc.get_project(name) for name in project_names]
    for project in projects:
        toc.configure_project(project)


    # qibuild.toc

    class Toc:

        def configure_project(self, project):
            qibuild.project.bootstrap_project(project, self)


    # qibuild.project.bootstrap_project

    def bootstrap_project(project, toc):

      config = toc.active_config
      if config:
          local_dir = os.path.join(toc.work_tree, ".qi")
          local_cmake = os.path.join(local_dir, "%s.cmake" % config)

      sdk_dirs = toc.get_sdk_dirs(project.name)




Using the toc object it is easy to find the custom cmake file
(see :ref:`parsing-custom-cmake-file`).

And then we use toc.get_sdk_dirs to find the list of SDK and write the
dependencies.cmake file

.. code-block:: cmake

    include(/path/to/worktree/<config>.cmake)

    list(INSERT 0 CMAKE_FIND_ROOT_PATH /path/to/world/sdk)


Why does it work ?
------------------


This works if ``world`` was created with

.. code-block:: cmake

    qi_create_lib(world)
    qi_stage_lib(world)


This way we can know that ``world-config.cmake`` will be in
``src/world/build/sdk/cmake/world-config.cmake``.


So, we are able to generate a ``dependencies.cmake`` in ``hello/build/`` looking like

.. code-block:: cmake

    list(INSERT 0 CMAKE_FIND_ROOT_PATH "src/world/build/sdk")


Also, the ``hello`` CMakeList.txt must contains

.. code-block:: cmake

    find_package(qibuild)

And inside ``qibuild-config.cmake`` we have

.. code-block:: cmake

    if(EXISTS ${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake)
      include(${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake)
    endif()



Getting the list of SDK dirs
-----------------------------

Let's have a closer look at this function:


.. code-block:: python


    # qibuild.toc

    class Toc:

        def get_sdk_dirs(self, project):

            dep_solver = DependenciesSolver(
                projects=self.projects,
                packages=self.packages,
                active_projects=self.active_projects)
            (r_project_names, _package_names, not_found) = dep_solver.solve([project_name])

            for project_name in r_project_names:
                project = self.get_project(project_name)
                dirs.append(project.get_sdk_dir())

          return dirs

But why do we use an **other** dependency solver here?

Two reasons:

First pathological case
+++++++++++++++++++++++

Assume you have no ``world`` package, but you run

.. code-block:: console

    qibuild configure -s

from ``hello`` source tree.

Here is what is going to happen:

``_projects_from_args`` will use the current working directory to find that
the project name is ``["hello"]``

``toc.use_deps`` will be set to False, so  ``toc.resolve_deps`` will only return
``["hello"]``, although qibuild knows that there is a ``world`` project on
which ``hello`` depends.

but, when solving deps inside ``toc.get_sdk_dirs``, we will still find the
``world`` dependency, and the ``dependencies.cmake`` will still be generated correctly.

Second pathological case
++++++++++++++++++++++++


Assume you have a ``hello`` package that depends on the ``world`` package
that itself depends on the ``foo`` package.

The ``dependencies.cmake`` (will be different for the three projects:


.. code-block:: cmake

    # hello/build/dependencies.cmake

    list(INSTERT 0 CMAKE_FIND_ROOT_PATH world/build/sdk)
    list(INSTERT 0 CMAKE_FIND_ROOT_PATH foo/build/sdk)

    # world/build/dependencies.cmake
    list(INSTERT 0 CMAKE_FIND_ROOT_PATH foo/build/sdk)

    # foo/build/dependencies.cmake
    # nothing


That's why the ``toc.get_sdk_dirs`` is called by each project.




.. _parsing-custom-cmake-file:

Parsing custom cmake file
--------------------------

This is mainly useful when you do continuous integration and releases.

For instance, we you just need to compile the ``hello`` project, you have
nothing to do.

But you may want to set ``-DCOVERAGE=TRUE`` for your nightly builds, or something
like that.

So to do that you have to have a way to have CMake code, but not put in the ``qiproject.xml`` file, because you only want to use those flags on certain occasions.

Note that sometimes you can even have complete piece of CMake code:


.. code-block:: cmake

  # Remove warnings about missing .pd on Visual Studio:
  set(_orig_flags ${CMAKE_CXX_FLAGS_DEBUG})
  string(REPLACE "/Zi" "" _package_debug_flags "${CMAKE_CXX_FLAGS_DEBUG}")
  set(CMAKE_CXX_FLAGS_DEBUG ${_package_debug_flags} CACHE INTERNAL "" FORCE)


So the convention is that you put you custom cmake code in ``.qi/<config>.cmake``.
