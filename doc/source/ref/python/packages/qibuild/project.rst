qibuild.project -- Managing :term:`projects <project>`
======================================================

.. py:module:: qibuild.project


qibuild.project.Project
-----------------------

.. autoclass:: qibuild.project.Project



Main attributes
++++++++++++++++

Those are set during initialization

.. attribute:: Project.name

   The name of the project

.. attribute:: Project.directory

    The source directory of the project

.. attribute:: Project.depends

    The list of build time depencies (read for qiproject.xml)

.. attribute:: Project.rdepends

    The list of runtime depencies (read for qiproject.xml)


Build related attributes:
+++++++++++++++++++++++++

Those need a :py:class:`toc instance <qibuild.toc.Toc>` to be correctly set,
add :py:func:`update_project` must have been called.

Here is a small example:

.. code-block:: console

   $ qibuild make --release foo

When this is  called, a ``toc`` ojbect is built with ``build_type=release``
and then the ``foo`` project and all its depencies are updated so
that they  contain ``-DCMAKE_BUILD_TYPE=RELEASE`` in their CMake flags.

.. attribute:: Project.cmake_flags

   CMake flags used.

.. attribute:: Project.build_directory

    The build_directory to use

.. attribute:: Project.sdk_directory

    Where to generate the build results. (By default
    in a 'sdk' directory inside the build directory,
    but use can choose to have a unique SDK dir for
    all projects)


Other functions in this module
------------------------------

.. autofunction:: update_project

    This will set the following attributes:

      * :py:attr:`project.cmake_flags <Project.cmake_flags>`
      * :py:attr:`project.build_directory <Project.build_directory>`
      * :py:attr:`project.sdk_directory <Project.sdk_directory>`

.. autofunction:: bootstrap_project

    This is to be called right before calling cmake
    inside the project build directory.

    Note that :py:func:`update_project` must have been called first,
    and then only can we use :py:meth:`toc.get_sdk_dirs <qibuild.toc.Toc.get_sdk_dirs>`

