.. _qibuild-python-doc:

qiBuild Python documentation
============================

Important
----------

qiBuild CMake API is **very** stable and retro-compatible. We try very
hard not to change the API.

qibuild command line API is also quite stable, but we may change the
command line syntax in the future.

The configuration files syntax changed a lot in the history of qibuild,
and it is possible it will change again. Most of the time, we will
provide an on-the-fly conversion of previous formats.

In comparison, the internal Python API is not at all frozen yet, and big
refactorings occurs all the time.

Use this documentation as a way to understand qibuild source
code, or hacking it, but please do not use qibuild as a Python library
for your own code, or be prepared to API changes.


qiBuild python packages
-----------------------


.. toctree::
   :maxdepth: 3

   packages/index


