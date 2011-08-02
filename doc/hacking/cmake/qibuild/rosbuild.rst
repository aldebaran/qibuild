QiBuild and rosbuild
====================

Introduction
------------

This tutorial is targeted towards rosbuild users wanting to know more about
QiBuild

General comparison
------------------

First, QiBuild and rosbuild have much in common.

They are both based on CMake, and provide a set of tools written in Python to
manage multiple projects, and dependencies between projects.

The CMake frameworks have both a public and a private API.

rosbuild is more used, has better documentation, and a large community. QiBuild
is still a work in progress :)

What is in QiBuild and not in rosbuild
--------------------------------------

* Automatic creation of installation rules.

* Ability to create redistributable, pre-compiled packages. (ROS supports
  generation of .deb packages, though)

* Strong cross-platform support. Supports both UNIX makefiles and Visual
  Studio projects. (Basically everything that is supported by CMake should run
  fine with QiBuild)

* Easy cross-compilation

* Handling of multiple build configurations with the same source directories.

* A bit less monolithic: the CMake framework can be used alone, (without the
  scripts), the redistributable packages can be used in pure CMake.

What is in rosbuild and not in QiBuild
--------------------------------------

* Automatic installation of dependencies (via rosdep scripts calling apt-get
  install)

* Parallel build of dependencies

* Nice shell features: nice output, auto-completion, roscd, etc...

* Tight coupling between rosmake (the build system), roslib (the library for
  communication), and generation of messages

* Nice Python support : automatic handling of $PYTHONPATH variable, rospython, ...

* Nice documentation

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

* Never tries to install anything, but uses libraries from the system when
  found.

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

  include(qibuild.cmake)
  qi_swig_wrap_python(_foo foo.i
    SRC bar.cpp
    DEPENDS ...)

Making the two play nice together
---------------------------------

Why?
++++

Nao’s users would be glad to be able to use the great Ros framework with their
robot.

Using qibuild's strong cross-platform support would be great for ros ! Ros
could become compatible with Visual Studio with reduced effort.

How?
++++

One way we could do it:

When qibuild is run from a source dir where there is a manifest.xml, it will

* create the qibuild.manifest file

* set ROS_ROOT to something like qibuild/cmake/qibuild/compat/

The rosbuild.cmake files then calls something like

.. code-block:: cmake

  include(qibuild/compat/ros/compat.cmake)

  function(ros_build_init)

    # other cmake magic can go here :)

    message(STATUS "Using qibuild!")
  endfunction()

  function(rosbuild_add_executable)

    # re-parse arguments
    ...
    qi_create_bin(_args)

  endfunction()


  function(rosbuild_genmsg)
    message(STATUS "not implemented yet!"
  endfunction()

This could be a nice first step to see how things go from there

