qisys.command - Launch processes
==================================

.. py:module:: qisys.command

Calling process
---------------

.. autofunction:: check_is_in_path

.. autofunction:: find_program

.. autofunction:: call

Notes about :py:func:`call`
++++++++++++++++++++++++++++

Finding the executable to run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using :py:func:`call(cmd, ...) <call>`,
:py:func:`check_is_in_path` is
always call with ``cmd[0]`` as argument, then replaced with the result
of :py:func:`find_program`.

This way, on Windows::

  qisys.command.call(["cmake", ...])

works as soon as ``cmake.exe`` is in ``PATH``


Behavior
~~~~~~~~~

`subprocess.Popen` is always called with ``shell=False``, for security
reasons.

Unless explicitly told not to, :py:class:`CommandFailedException` is raised
when the return code of the command is not zero.


Running process in the background
---------------------------------

.. autofunction:: call_background

.. autoclass:: Process


Exceptions
----------

.. py:class:: CommandFailedException
