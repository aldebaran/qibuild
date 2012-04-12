# qiBuild

This project aims to make compilation of cmake projects easy.
Please refer to the documentation for more information.

## git repository:
http://github.com/aldebaran/qibuild

## Mailing list:
https://groups.google.com/a/aldebaran-robotics.com/group/qibuild-dev/topics

## Documentation:
http://www.aldebaran-robotics.com/documentation/qibuild/index.html

## General installation:

There are two ways you can install qiBuild:

*  Default installation: Works as expected. qiBuild works after you installed it. It stops working until you remove it.
*  Installation by linking. qiBuild is run from source. If the source changes then the behaviour of qiBuild changes. qiBuild won't work if you move the source around. Propably only interesting for qiBuild developers.

### Default installation:

Archlinux users can take a look here: https://aur.archlinux.org/packages.php?ID=58398

The general approach is the same for all operating systems:

* Get a Python 2.7 installation for your operating system.
* Go to __../qibuild/python__ and run __python setup.py install__

See http://docs.python.org/install/index.html for a detailed description of the process.

### Installation by linking:

Linux, Mac:

* __./install-qibuild.sh__

Windows:

* Make sure __c:\Python27__ and __c:\Python27\scripts__ are in __%PATH%__ (Adapt these paths to reflect your Python's installation.)
* Run __install-qibuild.bat__

## qiBuild contains work from:

* argparse http://pypi.python.org/pypi/argparse/  (licensed under Python software foundation license version 2)
* xmlrunner http://www.rittau.org/python/xmlrunner.py (public domain)
* cmake http://www.cmake.org/cmake/project/license.html (BSD)
* gclient http://code.google.com/p/gclient/ (BSD)

##Maintainers:

* Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
* Cedric GESTES <gestes@aldebaran-robotics.com>
