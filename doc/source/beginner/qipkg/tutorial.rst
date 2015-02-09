.. _qipkg-tutorial:

qipkg tutorial
===============

``qipkg`` lets you make packages the same way Choregraphe does,
but from the command line, and also lets you embed code written in
C++ or Python inside the package

Usage
-----

First, you need a ``.pml`` file. Those are written by Choregraphe when
you save your project and look like this:

.. code-block:: xml


  <Package name="my-package">

    <!-- Some tags written and read by Choregraphe -->

  </Package>

A  ``manifest.xml`` should exist next to the pml file and should at least
contain ::

  <package version="0.0.1" uuid="my-package">

Those are the id and the version number used by the ``PackageManager`` on the robot

After that, just use:

.. code-block:: console

  qipkg make-package my-package.pml

to generate a package, and then (if libqi python bindings are available)

.. code-block:: console

  qipkg deploy-package /path/to/my-package.pkg --url nao@nao.local

to deploy and install the package on the robot.

If you need to include code written in C++ or Python, just add them to the
``.pml`` file, like this:

.. code-block:: xml

  <Package>

  <!-- choregraphe tags -->

    <qibuild name="foo" />
    <qipython name="bar" />

  </Package>

This assumes you have a ``qibuild`` CMake project named ``foo`` and a ``qipy`` project named
``bar`` in your worktree.

Also note that to include python projects in your package, you should have called ``qipy bootstrap`` at
least once.
