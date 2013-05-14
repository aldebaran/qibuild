Getting started with qibuild on Linux
======================================



Installing the compiler tools
-------------------------------

On ubuntu, this looks like

.. code-block:: console

  $ sudo apt-get install cmake build-essential

Refer to the documentation of your distribution for the details.

First run
---------

You should run

.. code-block:: console

   $ qibuild config --wizard

A file will be generated in ``~/.config/qi/qibuild.xml``.
It is shared by all the worktrees you will create.

You will be asked to choose a CMake generator.

It is advised to select ``Unix Makefiles`` unless you know what you are
doing :)

Building with QtCreator
-----------------------


See :ref:`qibuild-qtcreator`


Building with Eclipse CDT
--------------------------

Eclipse supports having distinct directories for the source and the build, but
does not like if the later is a subdirectory of the former.

So you have to use a global build directory, by editing
``QI_WORK_TREE/.qi/qibuild.xml`` to have

.. code-block:: xml

    <qibuild version="1">
      <build build_dir="/path/to/build/directory" />
    </qibuild>


Your project build directory will then be
``/path/to/build/directory/build-<config>/<project-name>``.

Or, if you chose a relative path, it will be relative to the
worktree.

You can also run ``qibuild config --wizard`` like this:

.. code-block:: console

   $ qibuild config --wizard
   :: Do you want to configure settings for this worktree (Y/n)
   y
   :: Do you want to use a unique build dir (mandatory when using Eclipse) (y/N)
   y
   :: Path to a build directory
   ~/workspace/build
   Will use /home/john/workspace/build as a root for all build directories


.. code-block:: console

   $ cd QI_WORK_TREE
   $ qibuild configure

Then from within eclipse, go to "File -> Import" then choose
"General -> General Projects into Workspace" and select your build directory
as "root directory". Let the "Copy projects into workspace" box unchecked
and click "Finish".
