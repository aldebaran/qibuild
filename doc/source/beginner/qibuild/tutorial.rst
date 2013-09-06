.. _qibuild-tutorial:

Building C++ projects with qibuild
===================================


Starting from scratch, you will:

* create some projects
* get a toolchain with some precompiled dependencies
* configure and build the projects
* deploy them to your robot


Installing and configuring qibuild
-----------------------------------

First make sure that ``qiBuild`` is installed correctly.
(see :ref:`getting-started`)

Open a console and type

.. code-block:: console

  qibuild --version

Then proceed with installing and configuring qibuild:

.. toctree::
    :maxdepth: 1

    getting_started/linux
    getting_started/mac
    getting_started/windows



Also install ``CMake`` and the various tools for compiling

If you are using the latest Ubuntu, you should install python2 by
hand first.

.. code-block:: console

  sudo apt-get install python




Creating a worktree
--------------------

You need to chose a qibuild "worktree".

This path will be the root from where qiBuild searches to find the sources of
your projects.

In the following document, we will use the notation ``QI_WORK_TREE`` to refer
to this path.

Then go to this directory and run

.. code-block:: console

  $ qibuild init


This will create a new qiBuild configuration file in your working directory, in
``QI_WORK_TREE/.qi/qibuild.xml``.

This file contains settings that will only used by this worktree.

If you re-run ``qibuild config --wizard`` form a directory inside your worktree,
the wizard will ask you if you want to configure settings for this worktree.

Starting a new project from scratch
------------------------------------

* Create a :term:`worktree`. It is advised to use an empty folder as
  a worktree

.. code-block:: console

    $ cd /path/to/worktree
    $ qibuild init

* Create a new project

.. code-block:: console

    $ qisrc create foo


Configure and build the project
-------------------------------

.. code-block:: console

    $ qibuild configure foo
    $ qibuild make foo


Using an IDE
------------

If everything is configured properly, you should be able
to start the IDE by running:

.. code-block:: console

  $ qibuild open


Proceed with

.. toctree::

    ide/qtcreator
    ide/visual_studio


Using Aldebaran packages
-------------------------

See:

.. toctree::
  :maxdepth: 2

  aldebaran

Going further
-------------

Follow the :ref:`qibuild-guide`

Optional: install qicd
++++++++++++++++++++++


``qicd`` is a small shell function that lets you jump quickly
from one project to an other inside your wortkree.

If you have access to ``bash`` shell, you can patch your config file
in order to use ``qicd``

.. code-block:: sh

  function qicd {
    p=$(python -m 'qicd' $1)
    if [[ $? -ne 0 ]]; then
      return
    fi
    cd ${p}
  }

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


Strange XML error messages
++++++++++++++++++++++++++

qiBuild does not cope well with badly formatted XML.

For instance, if ``.config/qi/qibuild.xml``, is invalid,
you will get error messages like ::

  Could not parse config from /home/user/.config/qi/qibuild.xml
  Error was: Opening and ending tag mismatch: qibuild line 1 and ibuild, line 39, column 10

Here the best way to fix it is to edit the config file by hand, or remove it
and re-run the config wizard.
