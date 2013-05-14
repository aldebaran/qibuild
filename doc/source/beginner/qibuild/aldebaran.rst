.. _qibuild-using-aldebaran-packages:

Using qibuild with Aldebaran C++ SDKs
=====================================

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

Troubleshooting
----------------


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

   qitoolchain info

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
