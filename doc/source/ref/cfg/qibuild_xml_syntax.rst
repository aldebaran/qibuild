.. _qibuild-xml-syntax:

qibuild.xml configuration file syntax
=====================================


General
-------

There are two configuration files named ``qibuild.xml``

The first one is in ``.config/qi/qibuild.xml``.

It contains settings that will be shared across every worktree.

It is called the "global" configuration file.

The other is always found in the ``.qi`` directory
at the root of a :term:`worktree`

Note: the presence of the file is not necessary for qibuild
to find a work tree, only the ``.qi`` directory is used.


When using nested worktrees (not recommended), the first
``.qi/qibuild.xml`` file found is used.



Global configration file
------------------------

.. _qibuild-xml-global-node:

qibuild global node
~~~~~~~~~~~~~~~~~~~

The schema of the global xml file looks like this:

.. code-block:: xml

    <qibuild version="1">
      <build />
      <defaults>
        <env />
        <cmake />
      </defaults>
      <config name="config1">
        <env />
        <cmake />
      </config>

      <config name="config2">
        <env />
        <cmake />
      </config>

      <ide name="ide1">
      <ide name="ide2">
    </qibuild>


Note the ``version`` attribute of the ``qibuild`` node.
It will be used for backward compatibility in case the format syntax changes.

It accepts:

* One or zero :ref:`qibuild-xml-node-build`
* One or zero :ref:`qibuild-xml-node-defaults`
* Any number of :ref:`config nodes <qibuild-xml-node-config>`
* Any number of :ref:`ide nodes <qibuild-xml-node-ide>`
* Any number of :ref:`server nodes <qibuild-xml-node-server>`

.. _qibuild-xml-node-build:

build node
~~~~~~~~~~

The build node accepts the following attributes:

**incredibuild**

  A boolean for triggering use of incredibuild (Visual Studio only)
  Will use ``BuildConsole.exe`` instead of ``cmake --build`` when
  building projects.

  For this to work qibuild must find ``BuildConsole.exe``, for instance
  you can add ``C:\Program Files\Xoreax\IncrediBuild\`` to a
  :ref:`qibuild-xml-node-env`.

.. _qibuild-xml-node-defaults:

defaults node
~~~~~~~~~~~~~

The defaults node accepts two kinds children:

* :ref:`qibuild-xml-node-env`
* :ref:`qibuild-xml-node-cmake`

It also accepts a 'ide' attribute, which should match
the 'name' attribute of a :ref:`qibuild-xml-node-ide`.

.. _qibuild-xml-node-env:

env node
~~~~~~~~

The 'env' node accepts the following attributes:

* 'path' : A list of paths to be prepended to the PATH environment variable
* 'bat_file: A .bat file that will be sourced to get new environment.
  Very useful to use ``cl.exe`` from the command line
* 'editor' : Used by ``qibuild config --edit``

.. _qibuild-xml-node-cmake:

cmake node
~~~~~~~~~~

The 'cmake' node accepts the following attributes:

**generator**

  The CMake generator to use

.. _qibuild-xml-node-config:

config node
~~~~~~~~~~~

The config node must contain a 'name' attribute.

It accepts the same kinds of children as the 'defaults' node does:

* :ref:`qibuild-xml-node-env`
* :ref:`qibuild-xml-node-cmake`


See :ref:`qibuild-config-merging` to see how the configuration
are merged

.. _qibuild-xml-node-ide:

ide node
~~~~~~~~

The 'ide' node must contain a 'name' attribute.

It accepts the following attributes:

**path**

  The full path to the IDE. Used by ``qibuild open`` when using
  QtCreator.

.. _qibuild-xml-node-server:

server node
~~~~~~~~~~~

The 'server' node must contain a 'name' attribute.

It accepts a child named 'access'.

The 'access' child accepts the following attributes:

* **username**
* **password**
* **root**
   When using ftp, this will be the root directory of
   the ftp server.

For instance to use 'john' username with password 'p4ssw0rd'
on ``ftp://example.com`` using root ``pub``, you can use

.. code-block:: xml

   <server name="example.com">
     <access
      username="john"
      password="p4ssw0rd"
      root="pub"
     />
  </server>



Local Settings
--------------

The schema of the local xml file looks like this:

.. code-block:: xml

    <qibuild version="1">
      <defaults />
      <build />
      <manifest />
    </qibuild>


Note the ``version`` attribute of the ``qibuild`` node.
It will be used for backward compatibility in case the format syntax changes.

The root element accepts:

* One or zero :ref:`qibuild-xml-node-local-defaults`
* One or zero :ref:`qibuild-xml-node-local-build`
* Any number of :ref:`manifest nodes <qibuild-xml-node-manifest>`


.. _qibuild-xml-node-local-defaults:

local defaults node
~~~~~~~~~~~~~~~~~~~

The local 'defaults' node accepts the following attributes:

**config**

  A configuration to use by default in this worktree
  (see :ref:`qibuild-config-merging`)

**ide**

  An IDE to use by default in this worktree. Can override
  the default ide in :ref:`qibuild-xml-node-defaults`
  (see :ref:`qibuild-config-merging`)

.. _qibuild-xml-node-local-build:

local build node
~~~~~~~~~~~~~~~~

The local 'build' nodes accepts the following attributes:

**build_dir**

  Instead of creating a different build directory per project,
  (for instance ``~/src/hello/build-linux``), every build
  directory will be created under this directory, for instance
  ``/path/to/build.directory/hello/build-linux``

  Mandatory if you are using Eclipse CDT.

**sdk_dir**

  This is useful when you want all your projects to use the
  same 'sdk' directory.

  This means that all the results of the compilation will end
  up in the same directory, rather that being spread over
  all the projects.


.. _qibuild-xml-node-manifest:

manifest node
~~~~~~~~~~~~~

The 'manifest' node must have a 'url' attribute.

For instance

.. code-block:: xml

   <manifest
      url="http://example.com/feed.xml
   />



.. _qibuild-config-merging:

Configuration merging
---------------------

Using "-c" option
~~~~~~~~~~~~~~~~~~

You may want to have several configurations for the same
work tree, and for instance have a ``vs2010`` and a ``mingw`` configuration.

In this case, the CMake generators will be different, so you
will need to have something like

.. code-block:: xml

  <qibuild version="1">
    <defaults>
      <cmake generator="Unix Makefiles" />
    </defaults>

    <config name="vs2010">
      <cmake generator="Visual Studio 10" />
    </config>

    <config name="mingw">
      <cmake generator = "MinGW Makefiles" />
    </config>
  </qibuild>



Here are the generators that will be used depending on the
configuration specified by the ``-c`` option of qibuild:

.. code-block:: console

   $ qibuild configure

   Using cmake generator: Unix Makefiles
   (from 'defaults' section)

   $ qibuild configure -c vs2010

   Using cmake generator: Visual Studio 10
   (from 'vs2010' config)

   $ qibuild config -c mingw

   Using cmake generator: MinGW Makefiles
   (from 'mingw' section)


A default configuration can be specified in the
:ref:`qibuild-xml-node-local-defaults` if you do not want
to have to specify ``-c`` for this worktree:

.. code-block:: xml

  <qibuild version="1">
    <defaults config="vs2010" />
  </qibuild>


Environment merging
~~~~~~~~~~~~~~~~~~~~

You may want to use ``swig`` in several projects, so you need to have
``swig.exe`` in your path, but sometimes you use ``QtCreator`` with MinGW,
so you need to have ``c:\QtSdk\Desktop\Qt\bin`` in your PATH too.

Here is what you could use:

.. code-block:: xml

    <qibuild version="1">
      <defaults>
        <env path="c:\swig\bin" />
      </defaults>

      <config name="mingw" />
        <env path="C:\QtSDK\bin" />
      </config>

      <config name="vs2010" />
    </qibuild>


* When using ``-c mingw``, ``%PATH%`` will look like:
  ``c:\swig\bin;C:\QtSDK\bin;...``

* When using ``-c vs2010``, ``%PATH%`` will look like:
  ``c:\swig\bin;...``


