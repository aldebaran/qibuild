##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics



clean(GSOAP)

fpath(GSOAP stdsoap2.h PATH_SUFFIXES gsoap)
flib(GSOAP gsoap)

export_lib(GSOAP)
