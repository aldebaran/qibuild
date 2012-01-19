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

First, get the C++ SKD and extract it, say in ``/path/to/cpp/sdk``

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

