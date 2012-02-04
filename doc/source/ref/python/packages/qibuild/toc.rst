qibuild.toc -- TOC means Obvious Compilation
============================================

.. py:module:: qibuild.toc



qibuild.toc.Toc
---------------

.. autoclass:: Toc


Since the class is huge, documentation of the Toc class
has been splitted in several parts:

* :ref:`toc-init`
* :ref:`toc-compilation-methods`
* :ref:`toc-configuration`
* :ref:`toc-dependencies-resolution`
* :ref:`toc-attributes`

.. _toc-init:

Initialisation
+++++++++++++++

.. automethod:: Toc.__init__


.. _toc-dependencies-resolution:

Dependency resolution
+++++++++++++++++++++

.. automethod:: Toc.resolve_deps


.. _toc-compilation-methods:

Compilation related methods
+++++++++++++++++++++++++++

Note : to use these method you must have a valid
:py:class:`qibuild.project.Project` instance.

You can get one using :py:meth:`Toc.get_project` method

.. automethod:: Toc.get_project

.. automethod:: Toc.get_sdk_dirs

.. automethod:: Toc.configure_project

.. automethod:: Toc.build_project

.. automethod:: Toc.install_project

.. automethod:: Toc.test_project

.. _toc-attributes:

Attributes
+++++++++++

This is only a small list of :py:class:`Toc` attributes.

.. py:attribute:: Toc.active_config

   See :ref:`toc-configuration`

.. py:attribute:: Toc.config

   A :py:class:`qibuild.config.QiBuildConfig` instance.

.. py:attribute:: Toc.projects

   List of objects of type :py:class:`qibuild.project.Project`
   this is updated using :py:attr:`qibuild.worktree.WorkTree.buildable_projects`

.. py:attribute:: Toc.toolchain

   A :py:class:`qitoolchain.toolchain.Toolchain` instance.
   Will be built from the active configuration name.

   Thus, ``self.toolchain.toolchain_file`` can be passed as
   `-DCMAKE_TOOLCHAIN_FILE` argument when calling
   :py:meth:`configure_project`, and
   ``self.toolchain.packages`` can be used to install contents
   of binary packages when calling :py:meth:`install_project`


.. _toc-configuration:

Toc configuration
-----------------

It always has a "current config". This config can be:

* None in the simplest case
* A default configuration specified in the current worktree
  configuration file (``.qi/qibuild.xml``)
* A configuration set by the user with the ``-c,--config`` of
  various qibuild command



Other functions in this module
------------------------------

qibuild.toc.toc_open
++++++++++++++++++++


.. autofunction:: qibuild.toc.toc_open

Typical usage from an action is:

.. code-block:: python

    def configure_parser(parser):
        # Add -c option
        qibuild.parsers.toc_parser(parser)

        # Add --release, --cmake-generator, -j options:
        qibuild.parsers.build_parser(parser)

        # Handle specifing zero, one or several project names
        # on the command line
        qibuild.parser.project_parser(parse)


    def do(args):
        toc = qibuild.toc.toc_open(args.work_tree, args)
        (project_names, _package_names, _not_found) = toc.resolve_deps()

        for project_name in project_nanes:
            project = toc.get_project(project_name)
            # Do something with 'project'


