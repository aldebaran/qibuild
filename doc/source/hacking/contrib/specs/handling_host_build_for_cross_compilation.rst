.. _handling-host-build-for-cross-compilation:

Handling host-build for cross-compilation
=========================================

Use case
--------

A project providing both data for the *target* and tools to generate this data.

So:

* the tools must be built to run on the *host*;

* the data generation, which is part of the cross-compilation run, should
  resolve the tools path;

qiBuild and CMake current state
-------------------------------

Currently, to cross-compile a project that depends on some *host-tools*, you
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

* CMake does not provide any way yet to express this *host build* paradigm when
  executing a cross-compilation.

* CMake does not allow to change the toolchain the during a build, nor use
  several toolchain in a build.

qiBuild
~~~~~~~

* qiBuild is executed at a higher level than CMake; qiBuild knows how to build
  projects' dependencies.

* qiBuild currently does not have any *host build* concept.

* qiBuild maintains separated staging areas (one per package and per build
  configuration).


Specifications
--------------

This RFC addresses the *host build* issue required to fully support
cross-compilation.

This issue can also be expressed  like this: *the cross-build of a project may
require some tools built for the host machine*. In other word a project may
depends on some *host-tools*.

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

* The dependency against some *host* tools/project should be declared in the
  ``qiproject.xml`` file:

  .. code-block:: xml

      <!-- qiproject.xml file -->
      <project name="bar">
        <depends buildtime="true" runtime="true" names="spam eggs" />
        <depends runtime="true" names="beans" />
        <depends host="true" names="toolbar" />
      </project>

* A project can depend on itself as a *host dependency*. In such case, this
  must be declared in the ``qiproject.xml`` file:

  .. code-block:: xml

      <!-- qiproject.xml file -->
      <project name="foo">
        <depends host="true" names="foo" />
      </project>

* The *host* dependencies will only be taken in account when using a
  cross-toolchain.

* When running a native build, the *host dependencies* are merged into the
  *buildtime dependency list*; the project itself dependency is dropped.

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

    #. first run the *host build* (ie. CMake configuration for the *host
       build* and native compilation),

    #. then run the *target build* (ie. CMake configuration for the *cross
       build* and cross-compilation).

* A toolchain should declare its type: *native* or *cross*, as any other
  package metadata.

* In every build, qiBuild must allow to specify the build configuration for the
  *target*:

  .. code-block:: console

      qibuild configure --config <target toolchain name>

* In *cross build*, qiBuild must allow to specify the *host build*
  configuration:

  .. code-block:: console

      qibuild configure --config <target toolchain name> \
        --host-config-name <host toolchain name>

* In *native build*, the *host build* configuration is the *target build*
  configuration, so it is not necessary to specify the former one.

* qiBuild should allow to associate a *host configuration* to a *target one*.

  .. code-block:: xml

      <!-- toolchain config file -->
      <config name="cross-arm">
        <toolchain name="arm_ctc"/>
        <host name="linux64"/>
      </config>

* qiBuild should allow to build for the *host* in *debug* and for the *target*
  in *release*, and vice-versa.

  The following examples mix debug/release between _host* and *target* builds:

  .. code-block:: console

      qibuild configure --config <target toolchain name> --release \
        --host-config-name <host toolchain name> --host-config-debug

      qibuild configure --config <target toolchain name> --debug \
        --host-config-name <host toolchain name> --host-config-release

* If the *host* build type is not set, qiBuild should use the same the *target*
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

* qiBuild should allow to use default *target configurations* and default *host
  configurations*; if not set, the default *host configuration* is the
  ``system`` toolchain:

  .. code-block:: console

      qibuild configure --config <target toolchain name>

  is equivalent to:

  .. code-block:: console

      qibuild configure --config <target toolchain name> \
        --host-config-name system

Notes
~~~~~

* qiBuild already knows if a toolchain is *native* or *cross*.

  A *cross-toolchain* (the cross-compiler package) has a ``host`` and a
  ``target`` metadata.

* For a project, a *host build* is a build whose the configuration uses the
  native compiler of the machine; in the simplest case, it the project will be
  built using the *system* toolchain.

* The *host* toolchain choice is solved like this:

  #. Use the *host* toolchain set on the command line, if not:

  #. Use the *host* toolchain set in the toolchain configuration file as
     property of the given *target* toolchain, if not:

  #. Use the *system* toolchain as the *host* toolchain.

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
