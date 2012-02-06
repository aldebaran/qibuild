.. _qibuild-managing-deps-overview:

Managing dependences with qiBuild: an overview
===============================================


Introduction
------------

Here we will use the same project layout we used in the
:ref:`qibuild-managing-deps` tutorial.

Make sure you have followed it before going further.

A quick reminder of what we want.

We have a project called ``world``, which contains a dynamic library also called
``world``. So we have a ``libworld.so`` on linux, and ``libworld.dylib`` on mac, and a
``world.dll`` on windows.

Then we have a project called ``hello``, which contains a executable also called
``hello``, which uses code from the ``world`` library.

Using the following two lines of cmake

.. code-block:: cmake

  qi_stage_lib(world)
  qi_use_lib(hello world)

we want to:

* add the correct include directories when building ``hello``

* link ``hello`` with the ``world`` library, without mixing a ``world`` library
  compiled in release with an ``hello`` executable compiled in debug (on windows at least)

* make sure that the ``hello`` executable will find the ``world`` library,
  without messing up with ``PATH``, ``LD_LIBRARY_PATH`` or ``DYLD_LIBRARY_PATH``

* generate a ``world-config.cmake`` so that the ``world`` library is usable by standard
  CMake project when installed.


Overview of the process: the power of the SDK layout
----------------------------------------------------

If you have a look at ``hello/qibuild.manifest,`` you will see the following lines

.. code-block:: ini

  [project "hello"]
  depends = world

Each time you run qibuild, it looks for a .qi to guess your current worktree.

After this, the worktree is parsed to find ``qibuild.manifest`` files.

Here, there are two ``qibuild.manifest`` files, so qibuild can find the two
projects: ``hello`` and ``world``.

The relevant lines of the ``CMakeLists.txt`` are:.

In ``world/CMakeLists``

.. code-block:: cmake

  qi_create_lib(world SRC world/world.h world/world.cpp)
  qi_stage_lib(world)

In ``hello/CMakeLists.txt``

.. code-block:: cmake

  qi_create_bin(hello "main.cpp")
  qi_use_lib(hello world)

.. note:: For those already familiar with CMake:
   We use :cmake:function:`qi_create_lib` and :cmake:function:`qi_create_bin` instead of
   ``add_executable`` and ``add_library``

  We never have to call ``find_package`` or ``include_directories``,  or
  ``target_link_libraries``.

This first part is the job is done by the :cmake:function:`qi_create_bin` and
:cmake:function:`qi_create_lib` functions.

Those are just wrappers for ``add_executable`` and ``add_library``.

They just set a few properties (like the ``RUNTIME_OUTPUT_LOCATION`` for instance).

There are other properties that are used so that the executable can find the
dynamic libraries it depends on at runtime, more on this later.

This way, we always generate binaries and libraries in the SDK directory. The
``build/sdk`` contains only the results of the compilation that are necessary to be
used by other projects.

Also, the executables are created in ``build/sdk/bin``, and the libraries in
``build/sdk/lib``, so that we stick to the FHS convention inside the
``build/sdk`` directory.

On Windows, the binaries compiled in debug contain ``_d`` in their names, so you
can share the same build directory, and the same Visual Studio solution for
several build configurations, without the risk of a mix of binaries compiled in
release and binaries compiled in debug.

This is done by something like

.. code-block:: cmake

  # in qibuild/general

  set(QI_SDK_DIR ${CMAKE_BINARY_DIR}/sdk)

  # in internal/layout:

  qi_set_global(QI_SDK_BIN "bin")
  qi_set_global(QI_SDK_LIB "lib")

  # then, in target.cmake

  set_target_properties(${name}
    PROPERTIES
      RUNTIME_OUTPUT_DIRECTORY ${QI_SDK_DIR}/${QI_SDK_BIN}
      RUNTIME_OUTPUT_DIRECTORY_RELEASE ${QI_SDK_DIR}/${QI_SDK_BIN}
      RUNTIME_OUTPUT_DIRECTORY_DEBUG ${QI_SDK_DIR}/${QI_SDK_BIN}
      ARCHIVE_OUTPUT_DIRECTORY ${QI_SDK_DIR}/${QI_SDK_LIB}
      LIBRARY_OUTPUT_DIRECTORY ${QI_SDK_DIR}/${QI_SDK_LIB}
      )

  if(WIN32)
    set_target_properties("${name}" PROPERTIES DEBUG_POSTFIX "_d")
  endif()

The call to :cmake:function:`qi_stage_lib` causes a ``world-config.cmake`` to be generated in
``world/build/sdk/cmake/``

When using ``qibuild configure hello``, a ``dependencies.cmake`` files is generated in
``hello/build/dependencies.cmake``

(this file is automatically included by the ``qibuild.cmake`` file at the root
of the ``hello`` project)

This file contains a call to

.. code-block:: cmake

  list(INSERT CMAKE_FIND_ROOT_PATH 0 "QI_WORK_TREE/world/build/sdk")

So when ``qi_use_lib(hello world)`` is called, we only have run

.. code-block:: cmake

  find_package(world)

Since the variable ``CMAKE_FIND_ROOT_PATH`` is correctly set, CMake can find the
``world-config.cmake`` file in the build dir of world.

Since everything under ``build/sdk`` follows the standard FHS conventions, finding
the library in ``sdk/lib`` is also works.


SDK and redistributable config files
------------------------------------

.. note:: you can see qibuild as a way to automatically follow the cmake conventions
  See the CMake wiki for more information

In fact we have two different ``world-config`` files.

The first one is installed. It is supposed to be used with a ``world`` pre-compiled
package, from an other machine than the one used to compile world. We call it
the **redistributable** config file.

The second one is generated in ``build/sdk/share/cmake/world/world-config.cmake``
so that CMake will find it if ``CMAKE_FIND_ROOT_PATH`` is set to ``build/sdk.`` We call it
the **SDK** config file.

There are several differences between the **redistributable** config file and the
**SDK** config file.

* The SDK file never has to call find_* functions: since we’ve just built the
  library, we know where it is. The redistributable file however must call
  ``find_library``, and ``find_path``.

* The SDK file uses absolute paths : we don’t care because we will never share
  this file with anyone. The redistributable file must only use relative paths to
  the root dir of the package.

This is how we can set ``ROOT_DIR`` to world-prefix from ``world-config.cmake``

We now we have a layout looking like::

  world-prefix
  |__ share
  |   |__ cmake
  |       |__ world
  |           |__ world-config.cmake
  |__ include
  |   |__ world
  |       |__ world.h
  |__ lib
      |__ libworld.so

So we generate the following code to set ROOT_DIR

.. code-block:: cmake

  get_filename_component(_cur_dir ${CMAKE_CURRENT_LIST_FILE} PATH)
  set(_root_dir "${_cur_dir}/../../../")
  get_filename_component(ROOT_DIR ${_root_dir} ABSOLUTE)

Calling qi_stage_lib
--------------------

The complete signature to :cmake:function:`qi_stage_lib` is in fact:


.. code-block:: cmake

  qi_stage_lib(prefix
    INCLUDE_DIRS  ...
    PATH_SUFFIXES ...
    DEFINITIONS   ...
    DEPENDS ...
  )

When flags are missing, we will guess them.

Note that prefix is always the name of a cmake target, i.e the first argument
of something like :cmake:function:`qi_create_lib`. There is an error message if you try to use
:cmake:function:`qi_stage_lib` on something that is not a target.

Let’s go through the variables one by one:

*<PREFIX>_INCLUDE_DIRS*
   only used in the sdk file. During the configuration of hello, we will simply
   call ``include_directories(WORLD_INCLUDE_DIRS)``

  If not given, this can be guessed using the "directory properties", like so:

.. code-block:: cmake

  get_directory_property(_inc_dirs INCLUDE_DIRECTORIES)

*<PREFIX>_PATH_SUFFIXES*
  only used in the redistributable file. The file will contain something like:

.. code-block:: cmake

  set(WORLD_INCLUDE_DIRS
    "${ROOT_DIR}/include"
    "${ROOT_DIR}/include/${WORLD_PATH_SUFFIXES}")

A few words about what this variable is for.

Let’s assume a client of the world library wants to use ``#include<world.h>``, but
``world.h`` is installed in ``world-prefix/include/world/world.h``

Other people, on the other hand, want to use ``#include<world/world.h>``.

The standard CMake way to deal with this is to call

.. code-block:: cmake

  find_path(WORLD_INCLUDE_DIR world.h PATH_SUFFIXES world)
  find_path(WORLD_INCLUDE_DIR world/world.h)

(hence the name of the variable)

This will never be guessed, because it’s too specific.

*<PREFIX>_DEFINITIONS*
  used by both config files. During the configuration of hello, we will simply
  call

.. code-block:: cmake

  set_target_properties(hello
    PROPERTIES
      COMPILE_DEFINITIONS "${WORLD_DEFINITIONS}"
  )

This will never been guessed. We could have done something like:

.. code-block:: cmake

  get_target_property(_world_defs world COMPILE_DEFINITIONS)

But most of the time you don’t have to propagate the compile flags everywhere.

*<PREFIX>_DEPENDS*
  used by both config files. If world depends on an thirdparty library (boost
  for instance), we want to make sure that whenever we use
  ``qi_use_lib(hello world)``, we also add the boost include directories.

Unless the ``world`` headers have been very carefully written, (using private
pointer implementations, forward declarations and the like), there’s a great
chance we will also need the boost headers when compiling ``hello,`` that’s why we
always propagate the dependencies by default.

This is guessed using the previous call to :cmake:function:`qi_use_lib`. In our example, after
using ``qi_use_lib(world boost)``, ``WORLD_DEPENDS`` contains "boost".

*<PREFIX>_LIBRARIES*
  used by both config files. In this case the SDK and the redistributable
  config file do not use the same code.

In the SDK file, we use something like:

.. code-block:: cmake

  get_target_property(_world_location world LOCATION)
  set(WORLD_LIBRARIES_world_location})

In the redistributable file, we use:

.. code-block:: cmake

  find_library(world ...)
  set(WORLD_LIBRARIES ...)

Calling qi_use_lib
-------------------

So what happens when using a :cmake:function:`qi_use_lib`?

When using ``qi_use_lib(foo bar)``, we will always call

.. code-block:: cmake

  find_package(bar)

But we have several cases here:

* We are using a ``bar-config.cmake`` that was generated by qibuild.

* We are using the custom ``bar-config.cmake`` in ``qibuild/cmake/modules``. This can
  happen because the upstream ``FindBar.cmake`` does not exist or is not usable. (For
  instance, the upstream ``FindGTest.cmake`` sets ``GTEST_BOTH_LIBRARIES,`` instead fo
  ``GTEST_LIBRARIES`` ...)

* We are using upstream’s CMake ``FindBar.cmake``.

To do this, we have to search for the `-config.cmake` files generated by qiBuild,
then fo look for upstream `Find-\*.cmake`


.. seealso::

   `CMake documentation of find_package
   <http://cmake.org/cmake/help/cmake-2-8-docs.html#command:find_package>`_

The relevant lines of code are:

.. code-block:: cmake

  find_package(${_pkg} NO_MODULE QUIET)
  find_package(${_pkg} REQUIRED)

.. note:: You can NOT specifiy optional dependencies when using qi_use_lib.

That’s because it’s hard to know from CMake wheter the foo-config.cmake file
was not found or the foo-config.cmake was found, the FOO_INCLUDE_DIRS was
found, but not the FOO_LIBRARIES). If you really want to have optional
depencies, you can do this this way:

.. code-block:: cmake

  find_package(FOO QUIET)

  if(FOO_FOUND)
    add_definitions(-DWITH_FOO)
    qi_use_lib(bar FOO)
  endif()
