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

Install ``qibuild`` with `pip <http://www.pip-installer.org/en/latest/>`_

.. code-block:: console

    pip install qibuild

Linux, mac
+++++++++++

It is recommended to install qibuild with ``pip install qibuild --user``
in order to keep your system clean.

If you do so, make sure that ``$HOME/.local/bin`` is in your ``$PATH``

Windows
+++++++


On windows, to use scripts written in Python, you have to put ``C:\Python2x`` and
``c:\Python2x\Scripts`` in your ``PATH``.


If you'd like to have nice colors in your console, you can install
the Python readline library: http://pypi.python.org/pypi/pyreadline


Continue with the tutorials
----------------------------


.. toctree::
    :maxdepth: 1

    qisrc/tutorial
    qisrc/templates
    qibuild/tutorial
    qidoc/tutorial
    qilinguist/tutorial
