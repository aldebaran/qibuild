##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics



clean(GETTEXT)

if(NOT WIN32)
  depend(GETTEXT REQUIRED DL)
endif()
fpath(GETTEXT libintl.h SYSTEM)

#dont find libintl on linux => libintl is part of glibc
if (NOT UNIX OR APPLE)
  flib(GETTEXT NAMES intl libintl intl.8.0.2)
endif (NOT UNIX OR APPLE)

if (NOT WIN32)
  flib(GETTEXT NAMES gettextpo gettextpo.0 gettextpo.0.4.0)
  flib(GETTEXT gettextsrc  gettextsrc-0.17)
  flib(GETTEXT gettextlib  gettextlib-0.17)
endif (NOT WIN32)

export_lib(GETTEXT)
