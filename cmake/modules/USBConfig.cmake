##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics

include("${T001CHAIN_DIR}/cmake/libfind.cmake")

clean(USB)
fpath(USB usb.h)
flib(USB usb)
export_lib(USB)
