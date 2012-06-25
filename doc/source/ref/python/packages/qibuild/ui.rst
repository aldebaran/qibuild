qibuild.ui -- Tools for the command line user interface
=======================================================

.. py:module:: qibuild.ui

Output messages for the user
----------------------------

.. autofunction:: error

.. autofunction:: warning

.. autofunction:: info

.. autofunction:: debug

You can use each of this functions as you would do for the
``print`` function in Python3.

To add colors, use the various colors defined in ``qibuild.ui``


Example ::


  from qibuild import ui

  ui.info(ui.green, "*", ui.bold, "(1/1)", ui.blue, project_name)



