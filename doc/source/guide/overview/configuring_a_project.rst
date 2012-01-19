.. _qibuild-configure-project:

Configuring a project
=====================

Configuring the foo project is done by:

.. code-block:: console

  $ qibuild configure foo

This command may be used anywhere under the QI_WORK_TREE directory.

You can also omit the project name if you are anywhere under the foo
directory:

.. code-block:: console

  $ cd foo
  $ qibuild configure

This will create a build directory in QI_WORK_TREE/foo/build, and run cmake in
this build directory.

(The name of the build directory reflects your platform and your configuration,
so that you can use different build configurations with the same source tree)

Building in release
-------------------

The project will be configured to build in debug by default.

If you want to build in release, use

.. code-block:: console

  $ qibuild configure --release

If you are not using Visual Studio, you will see that qibuild chose an other
build directory for you, ending with -release-.

Passing CMake flags
-------------------

To pass additional CMake flags, use:

.. code-block:: console

  qibuild configure -DFOO=BAR



Using Aldebaran packages
-------------------------


See: :ref:`qibuild-using-aldebaran-packages`
