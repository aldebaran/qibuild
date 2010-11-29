##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics



clean(CRYPTO)

fpath(CRYPTO ssl.h SYSTEM PATH_SUFFIXES openssl)

if(WIN32)
  flib(CRYPTO eay32)
  flib(CRYPTO SYSTEM ssleay32)
else(WIN32)
  flib(CRYPTO SYSTEM ssl)
endif(WIN32)
export_lib(CRYPTO)
