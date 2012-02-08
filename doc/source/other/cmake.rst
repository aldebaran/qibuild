.. _qibuild-and-cmake:

qiBuild and CMake
=================

Introduction
------------

This section is targeted to users already using CMake for their
build system.


.. seealso::

   * :ref:`porting-to-qibuild`

qiBuild is built **on top** of CMake.

Ultimately, every ``qi_`` functions call standard CMake functions, so for instance
:cmake:function:`qi_create_bin` accepts every argument the standard
``add_executable`` CMake function does.

After installing a qiBuild project, you can use the ``-config.cmake`` files generated
by qiBuild even from a pure CMake project.

A very high-level point of view
--------------------------------

One way to think about the ``qibuild`` is to compare this two few samples

.. code-block:: cmake

    # Find some deps for the whole project
    find_package(foo COMPONENT spam eggs)

    # Add include path for every target in this file
    include_directories(${FOO_INCLUDE_DIRS})

    # Create a bar library
    add_library(bar bar.h bar.c)

    # Link the bar target with foo libraries
    # (both libfoo_spam.so and libfoo_eggs.so)
    target_link_libraries(bar ${FOO_LIBRARIES})

    # Create a baz library
    add_library(baz bar.h bar.c)

    # Link the baz target with foo libraries
    # (both libfoo_spam.so and libfoo_eggs.so)
    target_link_libraries(bar ${FOO_LIBRARIES})

    # Lots and lots of install rules

.. code-block:: cmake

    qi_create_lib(bar bar.h bar.c)

    # Find the SPAM component of foo,
    # add the foo/spam include directory, and only link with
    # libfoo_spam.so
    qi_use_lib(bar FOO_SPAM)

    # Find the EGGS component of foo,
    # add the foo/eggs include directory, and only link with
    # libfoo_eggs.so
    qi_use_lib(baz FOO_EGGS)

    # Install rules for bar, baz already created,
    # bar-config and baz-config generated and ready to be installed to

You can see than in fact everything in qibuild is close to a target:
we tie together the include directories and the libraries, making it easier to avoid
weird link errors (i.e the include directory was correct but you forget to link with
the library)

Also note how easy it is to make sure that someone using bar will only depend on ``FOO_SPAM``,
and not the whole ``FOO`` package.


CMake variables
---------------

To make sure you do not break qiBuild behavior you should manipulate
the CMAKE_FIND_ROOT_PATH and CMAKE_MODULE_PATH variables carefully.

For instance:

.. code-block:: cmake

    # This will break finding packages in the toolchain:

    set(CMAKE_FIND_ROOT_PATH "/path/to/something")

    # This won't:

    # (create an empty list if CMAKE_FIND_ROOT_PATH does not exist)
    if(NOT CMAKE_FIND_ROOT_PATH)
      set(CMAKE_FIND_ROOT_PATH)
    endif()
    list(APPEND CMAKE_FIND_ROOT_PATH "/path/to/something")


.. code-block:: cmake

    # This will break finding the qibuild framework
    #  include (qibuild/general) will no longer work

    set (CMAKE_MODULE_PATH "/path/to/something")

    # This won't
    # (create an empty list if CMAKE_FIND_ROOT_PATH does not exist)
    if(NOT CMAKE_MODULE_PATH)
      set(CMAKE_MODULE_PATH)
    endif()
    list(APPEND CMAKE_MODULE_PATH "/path/to/something")



CMake functions
---------------


Creating executables
++++++++++++++++++++


Using :cmake:function:``qi_create_bin`` will make sure that:

* The executable is generated in ``build/sdk/bin``

* An install rule is created to ``<prefix>/bin``

* On linux, rpath is set to ``$ORIGIN/../lib``


You can change this behavior using various ``NO_`` arguments
to :cmake:function:`qi_create_bin` (for instance ``NO_INSTALL``, ``NO_RPATH`` ...),
or simply call ``set_target_properties`` yourself



Creating libraries
++++++++++++++++++


Using :cmake:function:`qi_create_lib` will make sure that:

* If the library is static, it is generated in ``build/sdk/lib``

* If the library is shared, it is generated in ``build/sdk/bin`` on Windows,
  and in ``build/sdk/lib`` on Windows

* The install rules us created accordingly

* On linux, ``-fPIC`` is used so that you can use the static library
  inside a shared library

* On mac, the install name dir is set to ``@executable_path/../lib``


You can change this behavior using various ``NO_`` arguments
to :cmake:function:`qi_create_bin` (for instance ``NO_FPIC``, ``NO_INSTALL``
...), or simply call ``set_target_properties`` yourself

The library will be:

* built as a shared library on UNIX
* built as a static library on windows

You can can set ``BUILD_SHARED_LIBS=OFF`` to compile everything in static by
default.


Installing
++++++++++

Using :cmake:function:`qi_install` functions will make sure that:

* You will get an error if the files you want to install do not exist
  at configuration time, not at install time.


Exporting targets
+++++++++++++++++


The ``export()`` and ``install(EXPORT ...)``  command do exist in standard CMake
but they are a bit clumsy to use.

(See :ref:`qi-stage-lib-vs-export` for details)

In ``qibuild``, you have a much nicer API

.. code-block:: cmake

   qi_stage_lib(world)

   qi_use_lib(hello world)


Using :cmake:function:`qi_use_lib` in conjunction with :cmake:function:`qi_stage_lib` work in any of the following cases:

* world and hello are both targets in the same project

* world and hello are two targets in two different projects in the same :term:`worktree`
  (providing a small configuration file)

* world is a package in a :term:`toolchain`

* world is a library that has been fond by a custom qibuild module in
  `cmake/qibuild/modules/world-config.cmake`

* world is a library installed on the system that has been found by
  an upstream CMake module in  `/usr/share/cmake/modules/FindWorld.cmake`


Plus, :cmake:function:`qi_use_lib` will export sane defaults for you:

* include directories will be set to the last call to `include_directories`

* WORLD_DEPENDS will be set using the calls to :cmake:function:`qi_use_lib(world ...)`

And still, you will be able to stage different include directories or dependencies if you want.

Even better, you can still use standard CMake code:

.. code-block:: cmake

   find_package(world)

   include_directories(${WORLD_INCLUDE_DIRS})

   add_library(hello)

   target_libraries(hello ${WORLD_LIBRARIES})

You do not need to read the `world-config.cmake` because you *know* the
exported variables will always have the same name: `<target>_INCLUDE_DIRS` and `<target>_LIBRARIES`


qibuild and CTest
------------------


See :ref:`qibuild-ctest`


.. _qi-stage-lib-vs-export:

qi_stage_lib versus export
--------------------------

You may wonder why :cmake:function:`qi_stage_lib` does not use ``export``.

There are several reaons but the main reason is that we did not like the idea
of the "global CMake package registry".

One workflow we needed to support since the beginning was to be able to use the
same worktree to compile for two different targets (say ``linux64`` and
cross-compiling)

Also, ``export`` does not work that well when you want to work with several versions
of the same target (say ``master`` and a ``release-1.12`` branch).

You can kind of solve that using version numbers (in a FooConfigVersion.cmake) for instance,
but that's a bit clumsy too.
