Install data
============

Let’s assume the ``foo`` executable needs to read data from a file called ``foo.data``

When you install ``foo,`` you would like to have something looking like::

  <prefix>
  |__ bin
      |__ foo
  |__ share
      |__ foo
          |__ foo.data

So, create a folder named ``share/foo`` and put a file named ``foo.data`` in your
source tree.

Installing files
----------------


To install the files, simply use

.. code-block:: cmake

  qi_install_data(share/foo/foo.data SUBFOLDER foo)

Please note: how to make sure that the foo executable is able to find the
foo.data file is out of the scope of this documentation.

A more in-depth tutorial on installation is availabe here:
:ref:`cmake-installing`



