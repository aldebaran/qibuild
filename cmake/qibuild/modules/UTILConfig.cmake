##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics



clean(UTIL)
fpath(UTIL "utmp.h" SYSTEM)
flib(UTIL "util" SYSTEM)
export_lib(UTIL)
