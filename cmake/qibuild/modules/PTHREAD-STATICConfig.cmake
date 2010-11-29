##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics



clean(PTHREAD-STATIC)
fpath(PTHREAD-STATIC "pthread.h" SYSTEM)
flib(PTHREAD-STATIC "pthread" SYSTEM)
export_lib(PTHREAD-STATIC)
