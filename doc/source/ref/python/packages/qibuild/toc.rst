qibuild.toc -- TOC means Obvious Compilation
============================================

.. py:module:: qibuild.toc



qibuild.toc.Toc
---------------

.. py:class:: Toc(work_tree[ , path_hints=None, config=None, build_type="debug", cmake_flags=None, cmake_generator=None)

    This class inherits from :py:class:`qibuild.worktree.WorkTree`,
    so it has a list of projects.

    It contains "high-level" functions.

    Example of use:

    .. code-block:: python

        toc = Toc("/path/to/work/tree", build_type="release")

        # Look for the foo project in the worktree
        foo = toc.get_project("foo")

        # Resolve foo dependencies, call cmake on each of them,
        toc.configure_project(foo)

        # Build the foo project, building all the dependencies in
        # the correct order:
        toc.build_project(foo)


    It also manages build configurations (see :ref:`toc-configuration`)
    cmake flags (see :ref:`handling-cmake-flags`), and dependencies
    resolution.


    .. py:attribute:: toolchain

       A :py:class:`qitoolchain.toolchain.Toolchain` instance.
       Will be built from the active configuration name.

       Thus, ``self.toolchain.toolchain_file`` can be passed as
       `-DCMAKE_TOOLCHAIN_FILE` argument when calling
       :py:meth:`Toc.configure_project`, and
       ``self.toolchain.packages`` can be used to install contents
       of binary packages when calling :py:meth:`Toc.install_project`


    .. py:method:: resolve_deps([runtime=False])

        Return a tuple of three lists:
        (projects, package, not_foud), see :py:mod:`qibuild.dependencies_solver`
        for more information.

        Note that the result depends on how the Toc object has been built.

        For instance, assuming you have 'hello' depending on 'world', and
        'world' is also a package, you will get:

        (['hello'], ['world'], [])  if user used

        .. code-block:: console

           $ qibuild configure hello

        but:

        (['world', 'hello], [], []) if user used:

        .. code-block:: console

           $ qibuild configure world hello



Compilation related methods
+++++++++++++++++++++++++++


.. py:method:: Toc.configure_project(project[, clean_first=True)

      Call cmake with correct options.

      Few notes:

      * The cmake flags (``CMAKE_BUILD_TYPE``, or the ``-D`` args coming
        from ``qibuild configure -DFOO_BAR``) have already been passed
        via the toc object. See :py:func:`qibuild.toc.toc_open` and the
        ``qibuild.project.Project`` for the details.

      * If toolchain file is not None, the flag CMAKE_TOOLCHAIN_FILE
          will be set.

      * If clean_first is False, we won't delete CMake's cache.
        This is mainly useful when you are calling cmake NOT from
        `qibuild configure`.


.. py:method:: Toc.build_project(self, project[, incredibuild=False, num_jobs=1, target=None, rebuild=False])

    Build a project.

    Usually we will simply can ``cmake --build``, but for incredibuild
    we need to call `BuildConsole.exe` with an sln.

.. py:method:: Toc.test_project(self, project[, verbose_tests=False, test_name=None])

      Run ctest on a project

      :param verbose_tests: Print the output of the tests
        (calling ``ctest -VV``)
      :param test_name: If given and not None, run only this
        test name


.. py:method:: Toc.install_project(self, project, destdir[ , runtime=False)

    Install the project

    :param project: project name.
    :param destdir: destination. Note that when using `qibuild install`,
      we will first call `cmake` to make sure `CMAKE_INSTALL_PREFIX` is
      ``/``. But this function simply calls ``cmake --target install``
      in the simple case.
    :param runtime: Whether to install the project as a runtime
       package or not.
       (see :ref:`cmake-install` section for the details)

.. _toc-configuration:

Toc configuration
-----------------

It always has a "current config". This config can be:

* None in the simplest case
* A default configuration specified in the current worktree
  configuration file (``qibuild.cfg``)
* A configuration set by the user with the ``-c,--config`` of
  various qibuild command



Other functions in this module
------------------------------

qibuild.toc.toc_open
++++++++++++++++++++


.. py:function:: toc_open(worktree[, args=None)

   Creates a Toc object.

   :param worktree: The worktree to be used. (see :py:class:`qibuild.worktree.WorkTree`)
   :param args: an ``argparse.NameSpace`` object containing
    the arguments passed from the comand line.

   You should always use this function to call Toc methods from
   a qibuild :term:`action`.

   It takes care of all the options you specify from command line,
   and calls Toc constructor accordingly

