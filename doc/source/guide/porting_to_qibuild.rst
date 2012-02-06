.. _porting-to-qibuild:

Porting a CMake project to qiBuild
==================================

Requirements
------------

This tutorial assumes that you already have a CMake-based project.

We will see how qiBuild can help you writing less code, while staying
close to the "official" CMake recommendations when dealing with the
``Find<>.cmake`` or ``<>-config.cmake`` files.

.. FIXME: add relevant link in cmake wiki

In this tutorial, we will use a simple project called ``foobar``.

It is pure CMake code, there is a ``foo`` library, and a ``bar`` executable linking
with the ``foo`` library.

The sources of the pure CMake ``foobar`` project can be found here:
:download:`foobar_pure_cmake.zip </samples/foobar_pure_cmake.zip>`

Extract the archive in you qiBuild worktree, you should end up with something
like::

  .qi
  |__ qibuild.xml
  |__ foobar
      |__ CMakeLists.txt
      |__ libbar
          |__ CMakeLists.txt
          |__ bar
              |__ bar.h
              |__ bar.cpp
      |__ foo
          |__ CMakeLists.txt
          |__ main.cpp

A standard CMake project
------------------------

The standard ``CMakeLists.txt`` files for such a project look like this:

**CMakeLists.txt**

.. literalinclude:: /samples/foobar_pure_cmake/CMakeLists.txt
   :language: cmake

**libbar/CMakeLists.txt**

.. literalinclude:: /samples/foobar_pure_cmake/libbar/CMakeLists.txt
   :language: cmake

**foo/CMakeLists.txt**

.. literalinclude:: /samples/foobar_pure_cmake/foo/CMakeLists.txt
   :language: cmake


A few CMake limitations
-----------------------

* You have to specify install rules for every target

* If you move the ``bar`` library to an other directory, you will have to fix
  ``foo/CMakeLists.txt``

* You cannot use ``foobar`` as a subdirectory of a new project (because of the use
  of ``CMAKE_SOURCE_DIR``

* You have a standard layout when you install your targets::

    <prefix>
      |__ lib
          |__ libbar.a
      |__ bin
          |__ foo
      |__ include
          |__ bar
             |__ bar.hpp

But it has nothing to do with where targets are in your build directory. (``foo``
is somewhere in ``build/foo/`` and ``libbar.a`` in ``build/bar``).

* If you want to give a ``foobar`` SDK for someone working with Visual Studio,
  you will have to make sure ``libbar`` and ``foo`` contain a ``_d`` when there are build
  on debug (unless you are very careful, you cannot mix debug and release
  libraries on Visual Studio, so the ``_d`` is the safest way to do it)

* If you want other people to use the ``bar`` library from an other project, you
  will have to configure a ``bar-config.cmake`` looking like:

.. code-block:: cmake

  find_path(BAR_INCLUDE_DIR bar/bar.hpp)
  find_library(BAR_LIBRARY bar)

  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(bar
    DEFAULT_MSG
    BAR_INCLUDE_DIR
    BAR_LIBRARY)

  mark_as_advanced(${BAR_INCLUDE_DIR} ${BAR_LIBRARY})

(and of course create the install rule for the ``bar-config.cmake)``

* Then, someone willing to use the ``bar`` library from an other project can do:

.. code-block:: cmake

  find_package(bar)

  include_directories(${BAR_INCLUDE_DIRS})
  add_executable(myexe ...)
  target_link_libraries(myexe ${BAR_LIBRARIES})

This assumes that the person has installed the ``bar`` packaged somewhere CMake can
find it. (For instance in ``/usr/local/share/cmake/bar-config.cmake``), or that
he sets ``-DBAR_DIR``.

It the person also happens to have the ``foboar`` sources built somewhere, it
cannot use them...

Neither ``libbar`` or ``bar.hpp`` can be found by CMake: ``bar.hpp`` is hidden somewhere in the
sources of ``foobar,`` and ``libbar.a`` somewhere in the build directory of ``foobar,`` so
it is impossible to use the carefully home-made ``bar-config.cmake``, unless you
install ``libbar`` to ``/usr/local/lib/libbar.a`` for instance.

qiBuild to the rescue!
----------------------

The motivation for qiBuild is to help solve this CMake limitations with a
clean, easy way, while staying the more compatible possible with other CMake
projects.

Preparation
+++++++++++

Add a call to ``find_package(qibuild)`` file at the root of the project and have it included right
after the ``project()`` line.

.. code-block:: cmake

  cmake_minimum_required(VERSION 2.8)
  project(foobar)
  find_package(qibuild)


Note that you somehow have to find the ``qibuild-config.cmake`` find from you qibuild sources,
if ``qibuild`` is not installed on your system.

You can do that by:

* Using ``cmake -Dqibuild_DIR=/path/to/qibuild/cmake/qibuild``,

or:

* Create the ``qiproject.xml`` and use ``qibuild configure`` which will set
  the ``qibuild_DIR`` CMake variable for you.

Install rules
++++++++++++++

Replace the ``add_library`` by :cmake:function:`qi_create_lib`, and remove
the install rules to use :cmake:function:`qi_install_header`  instead:

.. literalinclude:: /samples/foobar_qibuild/libbar/CMakeLists.txt
    :language: cmake


Using :cmake:function:`qi_create_lib` and :cmake:function:`qi_install_header` will have
the following effects:

* The install rules will been properly generated for the library

* For the headers, you must choose a subfolder in which to put your headers.
  (otherwise, it is too easy to have conflicts, especially when you are
  generating a big SDK.) Unless you have a very good reason not to, please
  choose the same folder name to put you headers inside your source tree, and
  once your header is installed. (here, the ``bar`` argument of :cmake:function:`qi_install_header`
  matches the location of ``bar.hpp``: ``bar/bar.hpp``).

* A ``sdk`` directory will be created, with ``libbar`` in ``skd/lib``

.. seealso::

    * :ref:`cmake-install`

Using the bar library
+++++++++++++++++++++

Add the following line in ``libbar/CMakeLists.txt``:

.. code-block:: cmake

  qi_stage_lib(bar)

And replace code in ``foo/CMakeLists.txt`` to have

.. code-block:: cmake

  qi_use_lib(foo bar)

(no need to call ``include_directories`` or ``target_link_libraries`` anymore)

You should end up with

.. literalinclude:: /samples/foobar_qibuild/foo/CMakeLists.txt
    :language: cmake

So what happened?

Two versions of the ``foo-config.cmake`` file have been generated:

* The first one is in ``build/cmake/sdk/bar-config.cmake`` : this one is supposed
  to be installed. You can see it is only using relative paths to find the
  library.

* The second one is in ``build/sdk/cmake/bar-config.cmake`` : this one is supposed
  to be used inside your project: it contains absolute paths only.

So, since the layout in ``build/sdk`` is the same as the layout when the library is
installed, and since the ``foo-config`` file has been automatically generated
(along with the install rules), it makes no difference whether you want to find
the ``bar`` library you have just built in the ``foobar`` project, using the ``bar``
library you have just built in a other project, or using the installed ``bar``
library.

Finding the ``bar-config.cmake`` in ``foobar/build/skd`` from an other project is as
easy as:

.. code-block:: cmake

  list(APPEND CMAKE_FIND_ROOT_PATH "/path/to/foobar/build/sdk")

Finding the ``bar-config.cmake`` once bar has been installed in as easy as:

.. code-block:: cmake

  # No qiBuild required: the installed bar-config.cmake contains
  # no qibuild-specific code:

  find_package(bar)

  include_directories(${BAR_INCLUDE_DIRS})
  add_library(foo)
  target_link_libraries(${BAR_LIBRARIES})

  # Or, still using qibuild:
  qi_use_lib(... bar)


.. note:: We always generate variables in the form <PREFIX>_INCLUDE_DIRS
   and <PREFIX>_LIBRARIES (all upper case, no version number, plural form)

Conclusion
----------

This is what the final code looks like when you are done:


**CMakeLists.txt**

.. literalinclude:: /samples/foobar_qibuild/CMakeLists.txt
   :language: cmake

**libbar/CMakeLists.txt**

.. literalinclude:: /samples/foobar_qibuild/libbar/CMakeLists.txt
   :language: cmake

**foo/CMakeLists.txt**

.. literalinclude:: /samples/foobar_qibuild/foo/CMakeLists.txt
   :language: cmake


Less code, so many features !

* You have a nice layout in ``build/sdk``

* You can use the newly compiled bar library inside the ``foobar`` project, outside
  the ``foobar`` project, or using an installed ``foobar`` package with always the same
  line:

.. code-block:: cmake

  qi_use_lib(foo bar)

* You did not have to write any install rule.

* You did not have to write any ``bar-config.cmake.``

* You can build SDK packages for other people to use, even on Visual Studio,
  without handling all the annoying cross-platform stuff (for instance, on
  windows, the .dll must be generated next to the .exe otherwise the use has to
  set %PATH%, and so on...)

* It is still pure, standard CMake code: you did not have to use the qibuild
  script.

* Absolutely nothing has been generated in the source directory, ``build/sdk`` only
  contains the useful, re-distributable binaries (no .o here)


The final project can be found here:
:download:`foobar_qibuild.zip </samples/foobar_qibuild.zip>`

