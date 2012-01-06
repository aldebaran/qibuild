.. _qibuild-and-rosbuild:

qiBuild and rosbuild
====================

Introduction
------------

This section is targeted towards rosbuild users wanting to know more about
qiBuild

General comparison
------------------

First, qiBuild and rosbuild have much in common.

They are both based on CMake, and provide a set of tools written in Python to
manage multiple projects, and dependencies between projects.

The CMake frameworks have both a public and a private API.

What is in qiBuild and not in rosbuild
--------------------------------------

* Automatic creation of installation rules.

* Ability to create redistributable, pre-compiled packages. (ROS supports
  generation of .deb packages, though)

* Strong cross-platform support. Supports both UNIX makefiles and Visual
  Studio projects. (Basically everything that is supported by CMake should run
  fine with qiBuild)

* Easy cross-compilation

* Handling of multiple build configurations with the same source directories.

* Loosly coupling between the command line tools and the CMake framework:
  you can use qibuild script to build pure-cmake projects, you do not need
  the qibuild script to use CMake qibuild functions

* Close to CMake standards: packages made with qiBuild do NOT depend
  on the qibuild CMake framework.

* qitoolchain provides a clean way to package and use third-party dependencies
  without touching the system, which will work on any Linux distribution.

What is in rosbuild and not in qiBuild
--------------------------------------

* Parallel build of dependencies

* Nice shell features: nice output, auto-completion, roscd, etc...

* Tight coupling between rosmake (the build system), roslib (the library for
  communication), and generation of messages

* Nice Python support : automatic handling of $PYTHONPATH variable, rospython, ...


Table of equivalences
---------------------

Initialisation
++++++++++++++

rosbuild
^^^^^^^^

.. code-block:: cmake

  include($ENV{ROS_ROOT}/core/rosbuild/rosbuild.cmake)
  rosbuild_init()

Need a few environment variables to be set.

qibuild
^^^^^^^^

.. code-block:: cmake

  include(${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake)

User has to copy/paste a qibuild.cmake files everywhere, but this file can
update itself.

Code generation
+++++++++++++++

rosbuild
^^^^^^^^

.. code-block:: cmake

  rosbuild_genmsg()
  rosbuild_gensrv()

qibuild
^^^^^^^^

N/A : loose coupling between the messaging library and the build framework.
Could be implemented in qibuild/cmake ?

Output paths
++++++++++++

rosbuild
^^^^^^^^

.. code-block:: cmake

  set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin})

Output path is inside source dir.

qibuild
^^^^^^^^

N/A : automatically set. Default SDK layout.

Output path is inside build dir, in a directory named sdk/ (temporary build
results are NOT in build/sdk)

Adding executables
++++++++++++++++++

rosbuild
^^^^^^^^

.. code-block:: cmake

  rosbuild_add_executable()

qibuild
^^^^^^^^

.. code-block:: cmake

  qi_create_bin()

Adding libraries
++++++++++++++++

rosbuild
^^^^^^^^

.. code-block:: cmake

  rosbuild_add_library()

qibuild
^^^^^^^^

.. code-block:: cmake

  qi_create_lib()

Management of dependencies
++++++++++++++++++++++++++

rosbuild
^^^^^^^^

* Looks for dependencies using rosdep and manifest.xml

* Try to apt-get them when relevant

* Run make inside the source dirs of the "buildable" dependencies.

* make runs cmake which launches rospack to get the compile flags and include
  dirs.

qibuild
^^^^^^^^

* Looks for dependencies using qibuild and qibuild.manifest

* Never tries to install anything, uses libraries from the system when
  found or can use pre-compiled packages with qitoolchain.

* Runs cmake inside the source dirs of the buildable dependencies, during
  qibuild configure, then cmake --build inside the build directories of the
  buildable dependencies, during qibuild make

Interface with other build systems
++++++++++++++++++++++++++++++++++

rosbuild
^^^^^^^^

rospack : command line tool, may be used by any build system

qibuild
^^^^^^^^

* generates and installs standard CMake files, usable by any CMake based
  projects. (implementing a rospack like functionality would not be hard,
  though)

Boost dependency
++++++++++++++++

rosbuild
^^^^^^^^

.. code-block:: cmake

  rosbuild_add_boost_directories()
  rosbuild_link_boost(${PROJECT_NAME} thread)

qibuild
^^^^^^^^

.. code-block:: cmake

  qi_use_lib(myproject BOOST_THREAD)

Easily do-able for other third-party libraries

Swig
++++

rosbuild
^^^^^^^^

.. code-block:: cmake

  include($ENV{ROS_ROOT}/core/rosbuild/rosbuild.cmake)
  rosbuild_init()
  find_package(PythonLibs REQUIRED)
  rosbuild_add_swigpy_library(python_foo foo foo_swig_generated.cpp bar.cpp)
  target_link_libraries(python_foo ${PYTHON_LIBRARIES})

qibuild
^^^^^^^^

.. code-block:: cmake

  include(qibuild/swig/python)
  qi_swig_wrap_python(_foo foo.i
    SRC bar.cpp
    DEPENDS ...)


Using qiBuild with rosbuild
---------------------------

Patching qiBuild to be able to **compile** rosbuild projects is probably doable,
but maybe not that useful. (Why would rosbuild users want to change their build
system?)

What could be nice instead is to make it easy to use rosbuild pre-compiled
**packages** from qibuild projects, using for instance a toolchain feed so that
the rosbuild packages only have to be compiled once.

