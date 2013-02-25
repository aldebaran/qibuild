.. _qibuild-in-five-minutes:

qiBuild in five minutes
=======================

First, please make sure you have follow the :ref:`qibuild-getting-started`
tutorial.

Starting a new project from scratch
------------------------------------

* Create a :term:`worktree`. It is advised to use an empty folder as
  a worktree

.. code-block:: console

    $ cd /path/to/worktree
    $ qibuild init

* Create a new project

.. code-block:: console

    $ qibuild create foo


* Configure and build the foo project

.. code-block:: console

    $ qibuild configure foo
    $ qibuild make foo


.. _qibuild-using-aldebaran-packages:

Using Aldebaran packages
-------------------------


For the Desktop
+++++++++++++++

You can use the C++ packages on Visual Studio 2008 and 2010 (32 bits only),
Mac and Linux.

First, get the C++ SDK and extract it, say in ``/path/to/cpp/sdk``

* Create a :term:`worktree` inside the C++ SDK examples folder:

.. code-block:: console

    $ cd /path/to/cpp/sdk/examples
    $ qibuild init


* Create a :term:`toolchain` using the :term:`feed` from the C++ SDK:

.. code-block:: console

    $ qitoolchain create naoqi-sdk /path/to/cpp/sdk/toolchain.xml


* Configure and build the helloworld project:

.. code-block:: console

    $ qibuild configure -c naoqi-sdk helloworld
    $ qibuild make -c naoqi-sdk helloworld



For the robot
++++++++++++++


You have to be on Linux to be able to compile code for the robot.
This if often refer to as ``cross-compilation``.

First, get the cross-toolchain that matches your robot
version (atom for V4 and later, geode for previous version),
and extract it, say in ``/path/to/atom/ctc``


.. note:: on linux64 you will have to install some 32bits libraries for the
          cross-compiler to work.

          On ubuntu, you should use something like:

          .. code-block:: console

              $ sudo apt-get install gcc-multilib libc6-dev libc6-i386


* Create a :term:`toolchain` using the :term:`feed` from the cross-toolchain

.. code-block:: console

    $ qitoolchain create cross-atom /path/to/ctc/


    $ qibuild configure -c cross-atom
    $ qibuild make -c cross-atom



Troubleshooting
---------------

Here are a few messages you can get, and a possible solution.


Configuration fails
++++++++++++++++++++

Usually the best way to know what is going wrong it to have
a look at the top of the error message, not the bottom...

Windows: cannot find specifed file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

qiBuild did not find ``cmake.exe.`` You have to make sure
``cmake.exe`` is in your ``PATH``.

You can do so during ``CMake`` installation, or re-run
``qibuild config --wizard`` to help qiBuild find it.


Cannot create generator 'Unix Makefiles'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This happens on windows. You have to tell qibuild to use
the 'Visual Studio' generator for instance.

See :ref:`qibuild-getting-started`

Cannot find alcommon
~~~~~~~~~~~~~~~~~~~~


::

  Could not find module FindALCOMMON.cmake or a configuration file for
  package ALCOMMON.

  Adjust CMAKE_MODULE_PATH to find FindALCOMMON.cmake or set ALCOMMON_DIR to
  the directory containing a CMake configuration file for ALCOMMON. The file
  will have one of the following names:

  ALCOMMONConfig.cmake
  alcommon-config.cmake


This happens because qibuild id not find the CMake files related to ``ALCOMMON``.

This can be because you did not add any toolchain to ``qibuild``
You can check with:

.. code-block:: console

   qitoolchain status

Output should look like ::

  toolchain naoqi-sdk
    Using feed from /path/to/naoqi-sdk-1.12-linux32/toolchain.xml
    Packages:
      naoqi-sdk-linux32
      in /path/to/naoqi-sdk-1.12-linux32

Here you can see that the toolchain is named ``naoqi-sdk``, so you have to:

* make sure qibuild uses the ``naoqi-sdk`` toolchain by default (you can do
  that by running the config wizard)

* or tell qibuild to use the ``naoqi-sdk`` toolchain:

.. code-block:: console

   $ qibuild configure -c naoqi-sdk
   $ qibuild make -c naoqi-sdk



Strange XML error messages
++++++++++++++++++++++++++

Right now qiBuild does not cope well with badly formatted XML.

For instance, if ``.config/qi/qibuild.xml``, you will get error messages
like ::

  Could not parse config from /home/dmerejkowsky/.config/qi/qibuild.xml
  Error was: Opening and ending tag mismatch: qibuild line 1 and ibuild, line 39, column 10

Here the best way to fix it is to edit the config file by hand, or remove it
and re-run the config wizard.
