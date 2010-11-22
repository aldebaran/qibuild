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


clean(URBICORE)
fpath(URBICORE urbi PATH_SUFFIXES urbicore)
fpath(URBICORE jconfig.h PATH_SUFFIXES urbicore)

flib(URBICORE uobject)

if(TARGET_HOST STREQUAL "TARGET_HOST_WINDOWS")
  flib(URBICORE libport)
endif(TARGET_HOST STREQUAL "TARGET_HOST_WINDOWS")

export_lib(URBICORE)
