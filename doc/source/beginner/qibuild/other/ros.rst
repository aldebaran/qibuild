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

Those CMake frameworks both have a public and a private API.

What is in qiBuild and not in the ROS build ecosystem
-----------------------------------------------------

* Ability to create redistributable, pre-compiled packages. (ROS supports
  generation of Ubuntu, Fedora, Homebrew packages, though)

* Easy cross-compilation

* qitoolchain provides a clean way to package and use third-party dependencies
  without touching the system, which will work on any Linux distribution.

What is in the ROS build ecosystem and not in qiBuild
-----------------------------------------------------

* ability to build sources in one common out of source build folder or in
  individual isolated build folders per projects.

* Parallel builds of projects as only one build space is usualy used.

* Python support : automatic handling of $PYTHONPATH variable, of ``setup.py``,
  no copy of sources

* special targets to build/run tests

* no need to use external tools to build the sources, you can call
  ``cmake && make`` from the command line after copying a specific
  ``CMakeLists.txt`` file

* tools to install/visualize dependencies

* workspace chaining: you can create several workspace with several project
  and use them by sourcing their ``setup.sh`` one after another

* a release tool to automatically bump versions, create .deb packages

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
explicitly, using standard CMake: nothing happens behind the scene. For
example, to use a catkin package, you need to call:


.. code-block:: cmake

  find_package(catkin COMPONENT foo)
  include_directories(${foo_INCLUDE_DIRS})
  target_link_libraries(bar ${foo_LIBRARIES})

The folder hierarchy is then a ``src`` folder with all your sources, and it stays
untouched. An out-of-source ``build`` folder that contains all the temporary files used
for building and an out-of-source/out-of-build ``devel`` folder that contains an
 FHS compliant set of built libraries and executables.

qibuild
^^^^^^^

With qibuild, you do not need to specify what you export as it is done
automatically when defining a library/executable:

.. code-block:: cmake

  qi_create_lib()
  qi_create_exe()

Using another package is then just a matter of calling:

.. code-block:: cmake

  qi_use_lib(bar FOO)

Each qiproject is built in the source folder in a ``build`` folder that is
proper to a specific toolchain.

Initialisation
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

Code generation
+++++++++++++++

catkin
^^^^^^

ROS includes some message generation packages in the ``genmsg`` package.
Generated ROS files can be of three types (action, services, messages) and are
of several bindings (whatever is installed but usually C++, Python, Lisp).

.. code-block:: cmake

  find_package(catkin REQUIRED genmsg ${MSG_PACKAGE_DEPENDENCIES})

  add_action_files(DIRECTORY ${ACTION_DIRECTORY} FILES ${ACTION_FILES})
  add_service_files(DIRECTORY ${SERVICE_DIRECTORY} FILES ${SERVICE_FILES})
  add_message_files(DIRECTORY ${MESSAGE_DIRECTORY} FILES ${MESSAGE_FILES})

  generate_messages(DEPENDENCIES ${MSG_PACKAGE_DEPENDENCIES})


qibuild
^^^^^^^

N/A : loose coupling between the messaging library and the build framework.
Could be implemented in qibuild/cmake ?

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

Management of dependencies
++++++++++++++++++++++++++

ROS
^^^

* Looks for dependencies using the catkin_pkg library and package.xml

* 3rd dependencies can be installed using rosdep, otherwise whatever is
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


Python support
++++++++++++++

catkin
^^^^^^

Catkin only cares about Python code declared in using setuptools (that includes
standard Python code, SWIG ...). Just write your ``setup.py`` and then call the
following macro from your ``CMakeLists.txt``.

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

Using qiBuild with the ROS build ecosystem
------------------------------------------

Patching qiBuild/ROS to be able to **compile** other projects is probably
doable, but maybe not that useful: a user probably just want to use one build
systme at a time.

On the other hand, if you compile ROS packages in their own workspace and source
the setup.sh, all environment variables are set to enable using ROS packages from
any CMake project, hence qiBuild projects too.
