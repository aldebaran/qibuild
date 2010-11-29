##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics



clean(ICONV)
fpath(ICONV iconv.h SYSTEM)

#only windows need iconv, on other plateform it's provided by the libc
if(NOT UNIX)
  flib(ICONV iconv)
  export_lib(ICONV)
else()
  export_header(ICONV)
endif()

