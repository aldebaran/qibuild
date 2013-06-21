.. _handling-host-build-for-cross-compilation:

[RFC] Handling host-build for cross-compilation
===============================================

Use case
--------

A project providing both data for the _target_ and tools to generate this data.

So:

* the tools must be built to run on the _host_;

* the data generation, which is part of the cross-compilation run, should
  resolve the tools path;

qiBuild and CMake current state
-------------------------------

Currently, to cross-compile a project that depends on some _host_-tools, you
must run something like:

.. code-block: console

    qc -p <tool project name>
    qm -p <tool project name>
    PATH=<tool project path>/build/sdk/bin
    qc -c cross -p <data project name>
    qm -c cross -p <data project name>


CMake
~~~~~

* CMake allows to search programs in some location, development files (headers
  and libraries) in others location.

* CMake does not provide any way yet to express this _host build_ paradigm when
  executing a cross-compilation.

* CMake does not allow to change the toolchain the during a build, nor use
  several toolchain in a build.

qiBuild
~~~~~~~

* qiBuild is executed at a higher level than CMake; qiBuild knows how to build
  projects' dependencies.

* qiBuild currently does not have any _host build_ concept.

* qiBuild maintains separated staging areas (one per package and per build
  configuration).


Specifications
--------------

This RFC addresses the _host build_ issue required to fully support
cross-compilation.

This issue can also be expressed  like this: _the cross-build of a project may
require some tools built for the host machine_. In other word a project may
depends on some _host-tools_.

So, some project may need to be built either:

* for the host machine only, it only provides host-tools;

* or for the target machine only;

* or for both the target and the host machine.

qiBuild/CMake already know how to run the first two builds in two distinct
runs.

This RFC is about handling these configurations of build in one run.

This RFC intends to address the issue at the qiBuild level, not at the CMake
one.

RFC keypoints
~~~~~~~~~~~~~

* CMake only needs to know one compiler (cross or native);

* No need to hack some CMake code to support this; so it will work out-of-box
  for existing CMake projects.

* This new property belongs to the project metadata, so will be stored in the
  ``qiproject.xml`` file.

* The dependency against some _host_ tools/project should be declared in the
  ``qiproject.xml`` file:

  .. code-block:: xml

      <!-- qiproject.xml file -->
      <project name="bar">
        <depends buildtime="true" runtime="true" names="spam eggs" />
        <depends runtime="true" names="beans" />
        <depends host="true" names="toolbar" />
      </project>

* A project can depend on itself as a _host dependency_. In such case, this
  must be declared in the ``qiproject.xml`` file:

  .. code-block:: xml

      <!-- qiproject.xml file -->
      <project name="foo">
        <depends host="true" names="foo" />
      </project>

* The _host_ dependencies will only be taken in account when using a
  cross-toolchain.

* When running a native build, the _host dependencies_ are merged into the
  _buildtime dependency list_; the project itself dependency is dropped.

  The following:

  .. code-block:: xml

      <!-- qiproject.xml file -->
      <project name="foo">
        <depends buildtime="true" runtime="true" names="eggs" />
        <depends buildtime="true" names="spam" />
        <depends host="true" names="toolbar foo" />
      </project>

  would behave like:

  .. code-block:: xml

      <!-- qiproject.xml file -->
      <project name="foo">
        <depends buildtime="true" runtime="true" names="eggs" />
        <depends buildtime="true" names="spam toolbar" />
      </project>

* In any build qiBuild first parses the projects' dependencies, then:

  * in native build, build (ie. CMake configuration and native compilation)
    just starts as usual.

  * in cross build, qiBuild will:

    #. first run the _host build_ (ie. CMake configuration for the _host
       build_ and native compilation),

    #. then run the _target build_ (ie. CMake configuration for the _cross
       build_ and cross-compilation).

* A toolchain should declare its type: _native_ or _cross_, as any other
  package metadata.

* In every build, qiBuild must allow to specify the build configuration for the
  _target_:

  .. code-block:: console

      qibuild configure --config <target toolchain name>

* In _cross build_, qiBuild must allow to specify the _host build_
  configuration:

  .. code-block:: console

      qibuild configure --config <target toolchain name> \
        --host-config-name <host toolchain name>

* In _native build_, the _host build_ configuration is the _target build_
  configuration, so it is not necessary to specify the former one.

* qiBuild should allow to associate a _host configuration_ to a _target one_.

  .. code-block:: xml

      <!-- toolchain config file -->
      <config name="cross-arm">
        <toolchain name="arm_ctc"/>
        <host name="linux64"/>
      </config>

* qiBuild should allow to build for the _host_ in _debug_ and for the _target_
  in _release_, and vice-versa.

  The following examples mix debug/release between _host_ and _target_ builds:

  .. code-block:: console

      qibuild configure --config <target toolchain name> --release \
        --host-config-name <host toolchain name> --host-config-debug

      qibuild configure --config <target toolchain name> --debug \
        --host-config-name <host toolchain name> --host-config-release

* If the _host_ build type is not set, qiBuild should use the same the _target_
  one.

  .. code-block:: console

      # will build both host and target in release:
      qibuild configure --config <target toolchain name> --release \
        --host-config-name <host toolchain name>

      # will build both host and target in debug:
      qibuild configure --config <target toolchain name> --debug \
        --host-config-name <host toolchain name>

      # will build both host and target using the default build type:
      qibuild configure --config <target toolchain name> \
        --host-config-name <host toolchain name>

* qiBuild should allow to use default _target configurations_ and default _host
  configurations_; if not set, the default _host configuration_ is the
  ``system`` toolchain:

  .. code-block:: console

      qibuild configure --config <target toolchain name>

  is equivalent to:

  .. code-block:: console

      qibuild configure --config <target toolchain name> \
        --host-config-name system

Notes
~~~~~

* qiBuild already knows if a toolchain is _native_ or _cross_.

  A _cross-toolchain_ (the cross-compiler package) has a ``host`` and a
  ``target`` metadata.

* For a project, a _host build_ is a build whose the configuration uses the
  native compiler of the machine; in the simplest case, it the project will be
  built using the _system_ toolchain.

* The _host_ toolchain choice is solved like this:

  #. Use the _host_ toolchain set on the command line, if not:

  #. Use the _host_ toolchain set in the toolchain configuration file as
     property of the given _target_ toolchain, if not:

  #. Use the _system_ toolchain as the _host_ toolchain.

Full example
------------

Given the following source tree:

.. code-block:: console

    barbooz/
    |-- qiproject.xml
    |-- data/
    |   |-- input01.xml
    |   `-- input02.xml
    |-- host-tools/
    |   `-- main.cpp
    |-- lib_io/
    |   |-- barbooz_io.hpp
    |   `-- barbooz_io.cpp
    `-- lib_engine/
        |-- barbooz_engine.hpp
        `-- barbooz_engine.cpp


The ``qiproject.xml`` could be:

.. code-block:: xml

    <project name="barbooz">
      <host>
        <depends buildtime="true" runtime="true" names="libqi opencv" />
      </host>
      <depends buildtime="true" runtime="true" names="boost libqi libnaoqi" />
      <depends runtime="true" names="naoqi" />
      <depends host="true" names="barbooz" />
    </project>

The CMakeLists.txt could be:

.. code-block:: cmake

    cmake_minimum_required(VERSION 2.8)
    find_package(qibuild)

    project(barbooz)

    # libbarbooz_io use by both generator and target library
    qi_create_lib(barbooz_io
      lib_io/barbooz_io.hpp
      lib_io/barbooz_io.cpp
    )
    qi_use_lib(barbooz_io
      ASSUME_SYSTEM_INCLUDE
      QI
    )
    qi_stage_lib(barbooz_io)

    # host-tools:
    qi_create_bin(barboozator
      generator/main.cpp
    )
    qi_use_lib(barboozator
      ASSUME_SYSTEM_INCLUDE
      OPENCV_CORE
      QI
    )
    qi_stage_bin(barboozator)

    # target stuff:
    qi_create_lib(barbooz
      lib_engine/barbooz_engine.hpp
      lib_engine/barbooz_engine.cpp
    )
    qi_use_lib(barbooz
      BARBOOZ_IO
    )
    qi_use_lib(barbooz
      ASSUME_SYSTEM_INCLUDE
      BOOST
      LIBNAOQI
      QI
    )

    # generate/install data
    find_program(barboozator)
    file(glob in data/*.xml)
    foreach f in ${in}
      ${generator} ${f} > ${f}.dat #sh-style :P
      qi_install_data(${f}.dat
        SUBFOLDER barbooz/data
      )
    endforeach()
