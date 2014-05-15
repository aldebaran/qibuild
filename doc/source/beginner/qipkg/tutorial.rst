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


  <package name="run_dialog">

    <!-- Some tags written and read by Choregraphe -->

  </package>

A  ``manifest.xml`` should exist next to the pml file and should at least
contain ::

  <package version="0.0.1" uuid="test_package">

Those are the id and the version number used by the ``PackageManager`` on the robot

After that, just use:

.. code-block:: console

  qipkg make-package my-behavior.pml

to generate a package, or even (if qimessaging python bindings are available)

.. code-block:: console

  qipkg deploy-package my-behavior.pml --url nao@nao.local

to call ``PackageManager.install()``

If you need to include code written in C++ or Python, just add them to the
``.pml`` file, like this:

.. code-block:: xml

  <package>

  <!-- choregraphe tags -->
    <qibuild name="foo" />
    <qipy name="bar" />

  </package>

This assumes you have a ``qibuild`` CMake project named ``foo`` and a ``qipy`` project named
``bar`` in your worktree.


