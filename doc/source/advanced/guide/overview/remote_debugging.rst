.. _qibuild-remote-debugging:

Remote debugging on NAO
=======================

.. warning:: This section is specific to Aldebaran cross-toolchains and the NAO
   robot.

In this section, we will assume you have already configured qibuild to use a
``geode`` cross toolchain, and that the IP of your robot is ``nao.local``

See the section :ref:`using-toolchains` for more details.

We will then show you how you can use ``qibuild deploy`` to upload the
code you have just cross-compiled to the robot, and then debug it.

Prerequisites
--------------

Since ``qibuild deploy`` uses ``ssh``, you should make sure you can
access your robot with ``ssh`` without typing your password over
and over and that ``rsync`` is installed.

.. code-block:: console

    ssh-keygen
    ssh-copy-id nao@nao.local


.. code-block:: console

    sudo apt-get install rsync


Running qibuild deploy
-----------------------

Here we will deploy all the code to a directory on the robot
named ``target``.

You can choose whatever directory you want.


Here's how you would compile and upload the ``sayhelloword``
example, for instance:

.. code-block:: console

    cd examples/core/sayhelloworld
    qibuild configure -c geode
    qibuild make -c geode
    qibuild deploy -c geode nao@nao.local:target

Here is what should happen:

* The project will be installed in a temporary directory named
  ``deploy`` inside the build directory.

* The debug symbols will be stripped from the binaries

* The ``deploy`` directory will be synchronized with the ``target``
  directory on the robot.

* Some gdb helpers script will be created.

At this point, you can look at the qibuild output messages to run
a gdb server on the robot, and then start using gdb from the command line
on your box.

But of course you may wish to use a IDE instead.

Using QtCreator
----------------

Remote debugging only has been tested with QtCreator, but the procedure
should be more or less the same for other IDEs.

* If you have not already, please read the section :ref:`qibuild-qtcreator`.

* Run the gdb server script on the robot:

.. code-block:: console

  $  /home/user/src/sayhelloworld/build-geode/deploy/remote_gdbserver.sh bin/sayhelloworld

  ....

  Server listening to 2159



* Open QtCreator and select the ``connect to a remote gdb server`` option

.. image:: /pics/qtcreator-remote-debugging-menu.png

* Configure the remote debugging settings:

.. image:: /pics/qtcreator-remote-debugging-setttings.png

.. warning:: You should select the binary in ``build-geode/deploy/bin``, **not**
              in ``build-geode/sdk/bin``

* And then start debugging as usual:

.. image:: /pics/qtcreator-remote-debugging.png

.. note:: The gdb server will exist as soon as the debug session ends.
          Simply rerun the script when this happens.

.. note:: The output of the program will be shown in the terminal where
          you ran the gdb server script.
