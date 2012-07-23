.. _qibuild-relnotes:

qiBuild release notes
=====================

What's new in qiBuild 1.16
---------------------------

general
+++++++

* Output of most commands are now more colorful and more readable

wortkree
++++++++


* better performances on all qibuild commands: paths of the projects are now stored in
  ``QI_WORKTREE/.qi/worktree.xml``

* buildable projects (directories containing a qiproject.xml and a CMakeLists
  are not automatically added to the project),
  Use ``qisrc add-project`` to add a new project to your worktree

* every buildable git project MUST have a qiproject.xml at the root. Il you
  have subprojet, you must add them this way:

.. code-block:: xml

  <project name="foo">
     <project src="gui" />
     <project src="lib" />
  </project>

qibuild
++++++++

* Add ``qibuild deploy`` to deploy code to a remote target, and easy
  remote debugging.

qisrc
+++++


* ``qisrc init`` now can be used with a git repository url, which lets you
  simply use several worktress with projects on different branches, or with
  different "profiles",

* new command to pull every repository, clone missing repositories, configure
  repositories  for code review called ``qisrc sync``

* support for code review with ``qisrc push``

qidoc
+++++

* ``qibuild doc`` can now be used to only build one project

* ``qidoc build`` used without arguments will:

 * build every doc when run at the top of the worktree
 * build only the current project if you are inside a directory of
   the project.
   For instance, running ``qidoc build`` running from ``qibuild/doc/source``
   will only build the doc for ``qibuild``)


* New command: ``qidoc open`` to view the generated documentation in a web
  browser

* ``qibuild doc`` used twice no longer re-compiles everything


qicd
++++

You can add the following to ``~/.profile`` on git bash or the equivalent
on linux

.. code-block:: bash

  source /path/to/qibuild/bin/qicd.sh

And then you can use

.. code-block:: console

  qicd libqi

To go directly to  ``lib/libqi``.

Note: the command will match the first basemane matching
the start of the argument ::

  qicd foo -> bar/foo
  qicd foo-g -> gui/foo-gui

cmake
+++++

* ``qibuild configure`` no longer creates a ``build-tests`` folder at the root of the project,
  the folder in whih the XML files are generated is now in ``build-<config>/test-results``

  .. seealso::

     * :ref:`qibuild-ctest`

Previous release notes
----------------------

* :ref:`qibuild-relnotes-1.14`
* :ref:`qibuild-relnotes-1.12.1`


Full Changelog
--------------

* :ref:`qibuild-changelog`
