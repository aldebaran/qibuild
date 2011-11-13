.. _qibuild-cfg-syntax:

qibuild.cfg configuration file syntax
=====================================


General
-------

The ``qibuild.cfg`` file is always found in the ``.qi`` directory
at the root of a ``QI_WORK_TREE``.

Note: the presence of the file is not necessary for qibuild
to find a work tree, only the ``.qi`` directory is used.


When using nested worktrees (not recommended), the first
``.qi/qibuild.cfg`` found file is used.


The file follows the synatx of the ``ConfigParser`` Python module.

.. code-block:: ini

   [general]
   cmake.generator = "Unix Makefiles"


Using configurations
--------------------


You may want to have several configurations for the same
work tree, and for instance have a ``vs2010`` and a ``mingw`` configuration.

In this case, the CMake generators will be different, so you
will need to have something like

.. code-block:: ini

  [general]
  cmake.generator = "Unix Makefiles"

  [config vs2010]
  cmake.generator = "Visual Studio 10"

  [config mingw]
  cmake.generators = "MinGW Makefiles"


Here are the generators that will be used depending on the
configuration specified by the ``-c`` option of qibuild:

.. code-block:: console

   $ qibuild configure

   Using cmake generator: Unix Makefiles
   (from 'general' section)

   $ qibuild configure -c vs2010

   Using cmake generator: Visual Studio 10
   (from 'config vs2010' section)

   $ qibuild config -c mingw

   Using cmake generator: MinGW Makefiles
   (from 'config mingw' section)


A default configuration can be specified in the ``[general]`` section:

.. code-block:: ini

   [general]
   config = vs2010



Known keys
----------

**env.editor**

  The editor to use. (By default on UNIX, **$EDITOR** will be used)

**env.ide.path**

  The IDE to use with ``qibuild open``.

  Not used with Visual Studio: we will simply call ``start
  path\to\project.sln``

**env.path**

  A list of colon or semi-colon separated to be added to the **PATH**
  environment when calling cmake or building projects.
  The spaces between colons will be stripped:

For instance on Windows:

.. code-block:: ini

  [general]
  env.path = c:\MinGW\bin;
             c:\Program Files\swig;

On UNIX:

.. code-block:: ini

  [general]
  env.path = ~/QtSDK/qtcreator/bin:
             /opt/swig/bin:

**env.bat_file**

  A .bat script that will be sourced to get the new environment.
  Very useful to use ``cl.exe`` from the command line

.. code-block:: ini

    [general]
    env.bat_file = c:\Program Files\Microsoft Visual Studio 9.0\VC\vcvarsall.bat

**build.directory**

  Instead of creating a different build directory per project,
  (for instance ``~/src/hello/build-linux``), every build
  directory will be created under this directory, for instance
  ``/path/to/build.directory/hello/build-linux``

  Mandatory if you are using Eclipse CDT.

**build.sdk_dir**

  This is useful when you want all your projects to use the
  same 'sdk' directory.

  This means that all the results of the compilation will end
  up in the same directory, rather that being spread over
  all the projects.

**build.incredibuild**

  Will use ``BuildConsole.exe`` instead of ``cmake --build`` when
  building projects.

  For this to work you must set the something like
  ``C:\Program Files\Xoreax\IncrediBuild\`` in ``PATH``, or use
  ``env.path`` configuration.


**cmake.generator**

  The CMake generator to use. Will be passed as-is to
  ``cmake -G`` when using ``qibuild configure``.

  You can get the full list currently supported by your CMake
  installation with ``cmake --help``

**manifest.url**

  The manifest to use when calling ``qisrc fetch``.
  Stored by ``qisrc fetch`` the first time it is called, so
  specifying the manifest URL is no longer necessary.

