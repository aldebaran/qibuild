.. _qibuild-host-tools:

Using host tools for cross compilation
=======================================

Say you have to generate sources during the build.
You do so using an executable called ``footool``.

In the tutorial we assume you have two configs:

* ``linux64``, associated to a toolchain containing for instance pre-compiled
  dependencies of ``footool``
* ``arm``, associated to a cross-toolchain targeting arm

The code looks like this:

.. code-block:: console

    worktree
      footool
        qiproject.xml
        CMakeLists.txt
        foo-config.cmake
        footool.cpp

.. code-block:: cpp

    // In footool.cpp

    int main(int argc, char* argv)
    {
      char* input = argv[1];
      char* output = argv[2];

      // Generate output from input

    }

.. code-block:: cmake

    # in CMakeLists.txt

    qi_create_bin(footool footool.cpp)
    qi_stage_bin(footool)

    qi_stage_cmake(foo-config.cmake)



    # in foo-config.cmake

    find_package(footool REQUIRED)

    function(generate_foo output input)

      qi_generate_src(${output}
        COMMAND ${FOOTOOL_EXECUTABLE} ${input} ${output}
      )

    endfunction()

You then have an other project which uses ``footool`` to generate some sources:

.. code-block:: console

    worktree
      footool
      usefootool
        qiproject.xml
        CMakeLists.txt


.. code-block:: cmake

    # In CMakeLists.txt

    find_package(foo REQUIRED)

    generate_foo(out src.cpp)

    # ...


So what you need is to configure and build the ``footool`` project so the binary
``footool`` exists, and find the ``footool`` executable in the build directory
of the ``footool`` project even when you are for instance cross-compiling.

To do so, you should:

* Patch the ``qiproject.xml`` to add a host dependency to ``footool``

.. code-block:: xml

    <!-- in usefootool/qiproject.xml -->
    <project version="3">
      <qibuild name="usefootool">
        <depends host="true" names="footool" />
      </qibuild>
    </project>

* Tell qibuild to use a ``host`` config.

  .. code-block:: console

    qibuild set-host-config linux64

* Configure and build the ``footool`` project:

  .. code-block:: console

      qibuild configure footool -c linux64
      qibuild make footool -c linux64


* Then you can cross-compile for arm:

  .. code-block:: console

      qibuild configure usefootool -c arm
      qibuild make usefootool -c arm

If you are not using any toolchain, you can of course just configure and build ``usefootool`` normally:

.. code-block:: console

    qibuild configure footool
    qibuild make footool

    qibuild configure usefootool -c arm
    qibuild make usefootool -c arm

* Alternatively, you can use ``qibuild make-host-tools`` from
  the ``usefootool`` directory. It will parse the host dependencies
  of the current build project and build them.

  .. code-block:: console

      cd usefootool
      qibuild make-host-tools
