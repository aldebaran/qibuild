.. _getting-started:

Getting Started
===============


Requirements
------------

qiBuild is a set of command line tools written in Python.
Only ``Python 2.7`` is supported.

Note that most linux distributions now comes with ``Python3``
by default now, so you may need to install ``python 2`` first.


Installation
------------

Get the source code from github: https://github.com/aldebaran/qibuild

Linux, mac
++++++++++

Simply run:

.. code-block:: console

  ./install-qibuild.sh

And make sure ``~/.local/bin`` is in your ``PATH``

Also install ``CMake`` and the various tools for compiling

If you are using the latest Ubuntu, you should install python2 by
hand first.

.. code-block:: console

  sudo apt-get install python

Windows
+++++++


On windows, to use scripts written in Python, you have to put ``C:\Python2x`` and
``c:\Python2x\Scripts`` in your ``PATH``.


Then run

.. code-block:: console

  install-qibuild.bat

If you'd like to have nice colors in your console, you can install
the Python readline library: http://pypi.python.org/pypi/pyreadline


Continue with the tutorials
----------------------------


.. toctree::
    :maxdepth: 1

    qisrc/tutorial
    qibuild/tutorial
    qidoc/tutorial
    qilinguist/tutorial
