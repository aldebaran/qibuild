.. _qibuild-and-rosbuild:

qiBuild and ROS build system
============================

Introduction
------------

This section is targeted towards ROS users wanting to know more about
qiBuild.

General comparison
------------------

First, qiBuild and the ROS build system have much in common.

They are both based on CMake, and provide a set of tools to
manage multiple projects, and dependencies between projects.

What is in qiBuild and not in the ROS build ecosystem
-----------------------------------------------------

* Ability to create redistributable, pre-compiled packages. (ROS supports
  generation of Ubuntu, Fedora, Homebrew packages, though)

* Easy cross-compilation (ROS only deals with cross-compilation through
  provided CMake but does not deal with extra packages and different build
  folders according to the architectures)

* qitoolchain provides a clean way to package and use third-party dependencies
  without touching the system, which will work on any Linux distribution (ROS
  deals with this by using existing infrastructures to create its own third
  party packages when needed)


What is in the ROS build ecosystem and not in qiBuild
-----------------------------------------------------

* ability to build sources in one common out of source build folder or in
  individual isolated build folders per projects.

* Parallel builds of projects when using one build space (default behavior).

* Python support : automatic handling of $PYTHONPATH variable, of
  ``setup.py``, no copy of sources during build

* special targets to build/run tests

* no need to use external tools to build the sources, you can call
  ``cmake ../ && make`` from the command line after copying a specific
  ``CMakeLists.txt`` file at the root of your workspace

* tools to install/visualize dependencies

* workspace chaining: you can create several workspaces with several projects
  and use them by chaining appropriate environment variables (which is done on
  Unix by sourcing a ``setup.sh`` file)

* a release tool ``bloom``, to automatically bump versions, create packages

CMake equivalences
------------------

Gist
++++

catkin
^^^^^^

Catkin never wraps any CMake functionality and only provides additional CMake
functionality. What you need to do in catkin is define what other packages need
to know about your package. This is done by calling one macro:

.. code-block:: cmake

  find_package(catkin)
  catkin_package(DEPENDS ${DEPENDENCY_NAMES}
                 INCLUDE_DIRS ${LIST_OF_INCLUDE_DIRS_TO_EXPORT}
                 LIBRARIES ${LIST_OF_LIBRARIES_TO_EXPORT}
  )

This will define the ``fooConfig.cmake`` and ``fooConfig-version.cmake`` files
that other packages will need. For everything else, you need to write things
explicitly, using standard CMake. For example, to use a catkin package, you
need to call:


.. code-block:: cmake

  find_package(catkin COMPONENT foo)
  include_directories(${foo_INCLUDE_DIRS})
  target_link_libraries(bar ${foo_LIBRARIES})

The folder hierarchy is then a ``src`` folder with all your sources, and it
stays untouched. An out-of-source ``build`` folder that contains all the
temporary files used for building and an out-of-source/out-of-build ``devel``
folder that contains an FHS compliant set of built libraries and executables.

qibuild
^^^^^^^

With qibuild, you do not need to specify what you export as it is done
automatically when defining a library/executable:

.. code-block:: cmake

  qi_create_lib()
  qi_create_bin()

Using another package is then just a matter of calling:

.. code-block:: cmake

  qi_use_lib(bar FOO)

Each qiproject is built in the source folder in a ``build`` folder that is
proper to a specific toolchain.

Initialization
++++++++++++++

catkin
^^^^^^

.. code-block:: cmake

  find_package(catkin)

qibuild
^^^^^^^

.. code-block:: cmake

  find_package(qibuild)

If ``qibuild`` is installed on the system, it just works,
but the qibuild command line tool is also smart
enough to pass ``-Dqibuild_DIR`` when necessary.

Output paths
++++++++++++

catkin
^^^^^^

Catkin lets you decide what you want to install and where using standard CMake.
For convenience, it defines variables you can reuse
(CATKIN_PACKAGE_BIN_DESTINATION, CATKIN_PACKAGE_SHARE_DESTINATION ...) and
that correspond to standard locations on your distro or OS.

.. code-block:: cmake

  install(${EXEC_TARGET} ${CATKIN_PACKAGE_BIN_DESTINATION})

The output path ``devel`` is outside the build dir and outside the source dir.

qibuild
^^^^^^^

N/A : automatically set. Default SDK layout.

Output path is inside build dir, in a directory named sdk/ (temporary build
results are NOT in build/sdk)

Adding executables
++++++++++++++++++

catkin
^^^^^^

Standard CMake:

.. code-block:: cmake

  add_executable()

qibuild
^^^^^^^

.. code-block:: cmake

  qi_create_bin()

Goes away from the CMake defaults:

* ``@rpath`` on mac (actual CMake 2.8.12 is going to do that by default too)
* install ``rpath`` set to ``$ORIGIN/../lib`` on Linux
* ``_d`` prefix on Visual Studio when building in debug
* install rules (force install in ``<prefix>/bin``)

Adding libraries
++++++++++++++++

catkin:
^^^^^^^

Standard CMake:

.. code-block:: cmake

  add_library()

qibuild
^^^^^^^

.. code-block:: cmake

  qi_create_lib()

Goes away from the CMake defaults:

* ``@rpath`` on mac (actual CMake 2.8.12 is going to do that by default too)
* install ``rpath`` set to relative to ``$ORIGIN`` on linux, so that
  ``dlopen(<prefix>/lib/plugin/foo.so)``  finds the dependencies in
  ``<prefix>/lib/libbar.so``

Management of dependencies
++++++++++++++++++++++++++

ROS
^^^

* Looks for dependencies using the ``catkin_pkg`` library and meta-info stored
  in a ``package.xml``

* 3rd party dependencies can be installed using rosdep, otherwise whatever is
  on the system is used.


qibuild
^^^^^^^

* Looks for dependencies using qibuild and qibuild.manifest

* Never tries to install anything, uses libraries from the system when
  found or can use pre-compiled packages with qitoolchain.

* Runs cmake inside the source dirs of the buildable dependencies, during
  qibuild configure, then cmake --build inside the build directories of the
  buildable dependencies, during qibuild make

3rd party dependencies
++++++++++++++++++++++

catkin
^^^^^^

Standard CMake:

.. code-block:: cmake

  find_package(Boost COMPONENTS thread)
  include_directories(${BOOST_INCLUDE_DIRS})
  add_library(${PROJECT_NAME} ${LIST_OF_SOURCE_FILES})
  target_link_libraries(${PROJECT_NAME} ${BOOST_LIBRARIES})

qibuild
^^^^^^^

.. code-block:: cmake

  qi_create_lib(${PROJECT_NAME} ${LIST_OF_SOURCE_FILES})
  qi_use_lib(myproject BOOST_THREAD)

Easy to use but requires the manual creation of one CMake file per 3rd party.
The flip side is that you can inherit dependencies:


.. code-block:: cmake

  qi_create_lib(foo)
  qi_use_lib(foo bar)
  qi_create_bin(baz)
  qi_use_lib(baz foo)  # baz links with foo and bar


(Something cmake 2.8.12 kinda does, but which much greater complexity
because they handle all the corner cases)

Python support
++++++++++++++

catkin
^^^^^^

Catkin only deals with Python using standard setuptools (and can therefore deal
with standard Python code, SWIG ...). Just write your ``setup.py`` and then
call the following macro from your ``CMakeLists.txt``.

.. code-block:: cmake

  catkin_python_setup()

Also, catkin does not copy your source Python files to the devel space to
avoid confusion and ease development: it creates ``__init__.py`` files that
refer to your sources.

qibuild
^^^^^^^

qiBuild has direct support for SWIG projects:

.. code-block:: cmake

  include(qibuild/swig/python)
  qi_swig_wrap_python(_foo foo.i
    SRC bar.cpp
    DEPENDS ...)

Using qiBuild with the ROS build ecosystem at the same time
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you create ROS packages in their own workspace and source the ``setup.sh``,
all environment variables are set to enable using those ROS packages from any
CMake project using ``find_package(catkin COMPONENTS foo)``, hence from qibuild
projects too.

qibuild projects have some limitations for now: they do not provide a
``fooConfig-version.cmake`` file yet, and need to be ``find_package()``-ed from
a qibuild project.
