qipkg
=====

-----------------------
Building NAOqi packages
-----------------------

:Manual section: 1

SYNOPSIS
--------
**qipkg** command

DESCRIPTION
-----------

Building NAOqi packages

COMMANDS
--------

Useful commands:

make-package PML_PATH
  Make a package using the information from the file in PML_PATH

deploy-package PACKAGE_PATH --url URL
  Deploy the package to the given URL. (Requires the pynaoqi Python SDK)
