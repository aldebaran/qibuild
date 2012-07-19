qiBuild
=======

This project aims to make compilation of cmake-based projects easy.
Please refer to the documentation for more information.

qibuild is under a BSD-style license that can be found in the COPYING file.
Any contribution is more than welcome ;)


git repository
--------------

http://github.com/aldebaran/qibuild

Mailing list
-------------

https://groups.google.com/a/aldebaran-robotics.com/group/qibuild-dev/topics

Documentation
-------------

http://www.aldebaran-robotics.com/documentation/qibuild/index.html

Installation
------------

Note that right now these methods are meant for qibuild git users only, so that
they can update qibuild by just pulling the git repository.

If you wish to package qibuild for your distribution, have a look
at the INSTALL file.

Linux, Mac
+++++++++++

Simply run::

  ./install-qibuild.sh

Windows
+++++++


* Make sure ``c:\Python27`` and ``c:\Python27\scripts`` are in ``%PATH%``
  (adapt these paths to reflect your Python's installation)

Then run::

  install-qibuild.bat


qiBuild contains work from
---------------------------

* argparse http://pypi.python.org/pypi/argparse/
  (licensed under Python software foundation license version 2)

* xmlrunner http://www.rittau.org/python/xmlrunner.py (public domain)

* cmake http://www.cmake.org/cmake/project/license.html (BSD)

* gclient http://code.google.com/p/gclient/ (BSD)

* pygments http://pygments.org/ (BSD)

Maintainers
------------

Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
Cedric Gestes <gestes@aldebaran-robotics.com>
