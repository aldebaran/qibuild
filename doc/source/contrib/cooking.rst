.. _qibuild-cooking:

What's cooking
--------------

General
++++++++

* Output of most commands are now more colorful and more readable

* The worktree is no longer scanned to find qibuild or qidoc projects,
  the paths are now stored in ``QI_WORKTREE/.qi/worktree.xml``, and you
  should use ``qisrc add <path>`` to register a path to your worktree.


* Every buildable project must now have ``qiproject.xml`` and a
  ``CMakeLists.txt`` at the root.
  You can create subprojects with

.. code-block:: xml

  <project name="foo">
     <project src="gui" />
     <project src="lib" />
  </project>


Transition from 1.14
++++++++++++++++++++

You should run:

.. code-block:: console

   $ qisrc init --auto-add

At the root of your 1.14 worktree to be able to use
the latest qibuild version.

At this point there is no automatic conversion planned.


qibuild
+++++++

* The argument parsing used for commands like ``qibuild configure``,
  ``qibuild make`` has changed:

  * Do not configure everything when running ``qibuild configure`` from an
    unknown subdirectory

  * Automatically add projects to the worktree when running ``qibuild
    configure`` for a project not yet added to the worktree

  * qibuild commands now accepts both project names and project paths

  * Now take both build dependencies and runtime dependencies into account by
    default. Use ``--build-deps`` to get only the build dependencies.


* Added ``qibuild deploy`` to handle deploying code to a remote device

  * Also generate gdb helper scripts for remote debugging

.. seealso::

    * :ref:`qibuild-remote-device`


qicd
+++++

To setup ``qicd``, add the following code to your
``~/.profile`` or equivalent:


.. code-block:: bash

  source /path/to/work/tools/qibuild/python/bin/qicd.sh

And then you can use ``qicd foo`` from anywhere in the
worktree to go to the ``foo`` project.

qisrc
++++++

* ``qisrc init`` must now be used with a git repository url, which lets you
  simply use several worktrees with projects on different branches, or with
  different "profiles"

* ``qisrc fetch`` is gone, use ``qisrc init`` instead

* ``qisrc pull`` is gone, use ``qisrc sync`` instead

* Add new command ``qisrc sync``:

  * Automatic support for code review with `gerrit <http://code.google.com/p/gerrit/>`_
  * Automatic support for git submodules.

* Add new command ``qisrc push`` to push changes to gerrit

cmake
+++++

* We find that ``qibuild configure`` can get a bit slow for large project,
  and we are trying to optimize that.

