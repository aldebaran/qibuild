##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

clean(URABALL)
fpath(URABALL "UraBall.h")
flib(URABALL "UraBall")
export_lib(URABALL)
