.. _qibuild-tips-and-tricks:

qiBuild tips and tricks
=======================

Here is a few collections of tips and tricks when using the qibuild framework

.. seealso::

   * :ref:`qibuild-cmake-coding-guide`
   * :ref:`CMake common mistakes <qibuild-cmake-common-mistakes>`

Use ``qibuild help``
--------------------

The builtin documentation is directly generated from the source code,
so it will always be accurate.

Trust it and use it!

You can use

.. code-block:: console

    qibuild help

To see a short description of all qibuild actions, and also

.. code-block:: console

   $ qibuild help <action>

To see the full help of the given action

Subdirectories order
--------------------

First of, a reminder: **you should never use subdirs, but use add_subdirectory
instead**

``subdirs`` is deprecated, and, worse, the parsing order when using ``subdirs``
is **not** defined!

Let's assume you have a ``foobar`` project, with two libraries, ``foo`` and
``bar``, with ``bar`` depending on ``foo``

You could end up write something like


.. code-block:: cmake

    # foobar/ CMakeLists.txt
    project(foobar)
    add_subdirectory(bar)
    add_subdirectory(foo)

.. code-block:: cmake

    # foobar/bar/CMakeLists.txt
    qi_create_lib(bar bar.cpp)
    qi_use_lib(bar foo)

.. code-block:: cmake

    # foobar/foo/CMakeLists.txt
    qi_create_lib(foo bar.cpp)
    qi_stage_lib(foo)


But then you will have this strange message:

.. code-block:: console

    $ qibuild configure foobar

    Could not find module FindFoo.cmake or a configuration
    file for package FOO.

    Adjust CMAKE_MODULE_PATH to find FindFOO.cmake or set
    FOO_DIR to the directory containing a CMake configuration
    file for FOO.  The file will have one of the following
    names:

    FooConfig.cmake
    foo-config.cmake


This strange message will magically go away the next time you run
``cmake`` or ``qibuild configure`` ...

Why?


Because CMake only parses the CMakeLists only once.

So by the time it gets through ``bar/CMakeLists.txt``,
it has not parsed ``foo/CMakeLists.txt`` yet, so the ``foo`` library
has not been staged yet.

But it does not stop the processing, and stages the ``foo`` library anyway ...


So the basic rule should be:

  *Always clean up build/sdk when changing CMake dependencies*



The fix is easy: make sure you stage the ``foo`` library **before** using it:

.. code-block:: cmake

    # foobar/ CMakeLists.txt
    project(foobar)
    add_subdirectory(foo)
    add_subdirectory(bar)

.. _qibuild-compile-warnings:

Compile warnings
-----------------

By default, ``qibuild`` will not change your compile flags at all.

If you work in a cross-platform environment, it is advised you
use :cmake:function:`qi_sanitize_compile_flags`

.. code-block:: cmake

   find_package(qibuild)
   qi_sanitize_compile_flags()

This will triggers compile warnings for all platform (cl.exe and gcc.exe)

You can then use

.. code-block:: console

   $ qibuild configure --werror

To make sure compile warnings will be treated as errors for any following
build of the same project.

