##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Jean-Charles DELAY <jdelay@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics



if(UNIX AND NOT APPLE)
  set(PCRE_IN_SYSTEM "SYSTEM")
else()
  set(PCRE_IN_SYSTEM "")
endif()

clean(PCRE)

fpath(PCRE pcre.h ${PCRE_IN_SYSTEM})
flib (PCRE pcre   ${PCRE_IN_SYSTEM})

export_lib(PCRE)
