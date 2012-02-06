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

Ultimately, every `qi_` functions call standard CMake functions, so for instance
`qi_create_bin` accepts every argument the standard `add_executable` CMake function does.

After installing a qiBuild project, you can use the `-config.cmake` files generated
by qiBuild even from a pure CMake project.

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


Using :cmake:function:`qi_create_bin` will make sure that:

* The executable is generated in `build/sdk/bin`

* An install rule is created to `<prefix>/bin`

* On linux, rpath is set to `$ORIGIN/../lib`


You can change this behavior using various ``NO_`` arguments
to `qi_create_bin` (for instance ``NO_INSTALL``, ``NO_RPATH`` ...),
or simply call `set_target_properties` yourself



Creating libraries
++++++++++++++++++


Using :cmake:function:`qi_create_lib` will make sure that:

* If the library is static, it is generated in `build/sdk/lib`

* If the library is shared, it is generated in `build/sdk/bin` on Windows,
  and in `build/sdk/lib` on Windows

* The install rules us created accordingly

* On linux, `-fPIC` is used so that you can use the static library
  inside a shared library

* On mac, the install name dir is set to `@executable_path/../lib`


You can change this behavior using various ``NO_`` arguments
to `qi_create_bin` (for instance ``NO_FPIC``, ``NO_INSTALL`` ...),
or simply call `set_target_properties` yourself

The library will be:

* built as a shared library on UNIX
* built as a static library on windows

You can can set BUILD_SHARED_LIBS=OFF to compile everything in static by
default.


Installing
++++++++++

Using :cmake:function:`qi_install` functions will make sure that:

* You will get an error if the files you want to install do not exist
  at configuration time, not at install time.


Exporting targets
+++++++++++++++++


The `export()` and `install(EXPORT ...)`  command do exist in standard CMake
but they are a bit clumsy to use.

In `qibuild`, you have a much nicer API

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


Plus, `qi_use_lib` will export sane defaults for you:

* include directories will be set to the last call to `include_directories`

* WORLD_DEPENDS will be set using the calls to `qi_use_lib(world ...)`

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
